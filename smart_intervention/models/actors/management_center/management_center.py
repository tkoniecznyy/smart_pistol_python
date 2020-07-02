import logging
from typing import Callable

from smart_intervention.simulation_variable_type import SimulationVariableType
from smart_intervention.globals import Notifications, CityMap, SimulationVariables
from smart_intervention.events.intervention_event import InterventionEvent
from smart_intervention.models.actors.bases import BaseActor
from smart_intervention.models.actors.management_center.management_center_notification import \
    ManagementCenterNotification
from smart_intervention.models.actors.management_center.management_center_notification_processor import \
    ManagementCenterNotificationProcessor
from smart_intervention.models.actors.management_center.management_center_resource_monitor import (
    ManagementCenterResourceMonitor,
    ResourceState,
)


# TODO: Add a event finished signal and process it from management center
# This would be a case of event cancellation or it being not-active anymore
# Can make other precautions instead

# TODO: Fix double dispatching when intervention is transitioned to gunfight

class ManagementCenter(BaseActor):

    def __init__(self, managed_units):
        self._resource_monitor = ManagementCenterResourceMonitor(managed_units)
        self.log = logging.getLogger(f'ManagementCenter#{id(self)}')

    def tick_action(self, notifications) -> Callable:
        processable_notifications = notifications.get_notifications_for_processing(self)

        def action():
            self.log.debug(f'Received {len(processable_notifications.get())} processable notifications')
            ManagementCenterNotificationProcessor(self).process(processable_notifications)
            interventions = CityMap.get_interventions()
            not_gunfight_interventions = [
                intervention for intervention in interventions
                if not intervention.armed_combat and intervention.active
            ]
            self._process_interventions(not_gunfight_interventions)

        return action

    def acknowledge_intervention(self, event, actor):
        self._resource_monitor.set_unit_state(actor, ResourceState.INTERVENTION, event)

    def acknowledge_gunfight(self, event, actor):
        self._resource_monitor.set_unit_state(actor, ResourceState.GUNFIGHT, event)

    def acknowledge_return_to_duty(self, actor):
        self._resource_monitor.set_unit_state(actor, ResourceState.AVAILABLE)

    def acknowledge_reject_ambulance_request(self, event):
        self._resource_monitor.set_ambulances_unavailable(event)

    def acknowledge_accept_ambulance_request(self, event, actor):
        self._resource_monitor.set_ambulance_state(actor, ResourceState.DISPATCHED, event)

    def process_backup_needed(self, event):
        if event.active:
            if not event.backup_sufficient:
                self._send_policemen_backup(event)

    def _send_policemen_backup(self, event):

        dispatched_efficiency = InterventionEvent.sum_ambulances_and_units_efficiency(
            self._resource_monitor.get_dispatched_ambulances(event=event),
            self._resource_monitor.get_dispatched_to_intervention_units(event=event)
        ) * SimulationVariables[SimulationVariableType.ROUNDS_TO_FINISH]
        missing_efficiency = (event.missing_efficiency - dispatched_efficiency) * (1 + SimulationVariables[
            SimulationVariableType.REDUNDANCY_OF_MANPOWER
        ])
        # Firstly check, if we even need more dispatched units
        if missing_efficiency > 0:
            self.log.debug(f'Searching for available policemen for event {id(event)}')
            policemen = []
            # First - take policemen which are available
            available_policemen = self._resource_monitor.get_available_units()
            missing_efficiency = self._take_close_policemen(
                missing_efficiency, event.location, available_policemen, policemen
            )

            if missing_efficiency > 0:
                self.log.debug(f'Searching for policemen dispatched to intervention for event {id(event)}')
                # Then - take policemen which are dispatched to intervention
                dispatched_policemen = self._resource_monitor.get_dispatched_to_intervention_units()
                missing_efficiency = self._take_close_policemen(
                    missing_efficiency, event.location, dispatched_policemen, policemen
                )
                self._dispatch_ambulance(event)

                if missing_efficiency > 0:
                    self.log.debug(f'Searching for intervening policemen for event {id(event)}')
                    # Last resort - take policemen which are intervening
                    intervening_policemen = self._resource_monitor.get_intervening_units()
                    self._take_close_policemen(
                        missing_efficiency, event.location, intervening_policemen, policemen
                    )
            if policemen:
                self.log.info(f'Sending policemen to gunfight intervention {id(event)}')
                for policeman in policemen:
                    self._dispatch_to_gunfight(policeman, event)
            else:
                self.log.info(f'No available units found to dispatch to gunfight {id(event)}')

    def _take_close_policemen(self, missing_efficiency, location, policemen_pool, policemen_to_take):
        policemen = self._by_proximity(policemen_pool, location)
        while missing_efficiency > 0 and policemen:
            next_policeman = policemen.pop(0)
            policemen_to_take.append(next_policeman)
            missing_efficiency -= next_policeman.efficiency
        return missing_efficiency

    @staticmethod
    def _by_proximity(units, location):
        policemen_distances = [
            (CityMap.get_distance(policeman.location, location), policeman)
            for policeman in units
        ]
        policemen_distances.sort(key=lambda x: (x[0], x[1].efficiency))
        return [tpl[1] for tpl in policemen_distances]

    def _process_interventions(self, interventions):
        for intervention in interventions:
            dispatched_units = self._resource_monitor.get_dispatched_to_intervention_units(intervention)

            if not intervention.dispatched_backup_sufficient(dispatched_units):
                self.log.info(f'Seeking for backup for intervention event {id(intervention)}')
                send_policemen = []
                available_policemen = self._resource_monitor.get_available_units()
                self._take_close_policemen(
                    intervention.missing_efficiency, intervention.location, available_policemen, send_policemen
                )
                for policeman in send_policemen:
                    self._dispatch_to_intervention(policeman, intervention)
                if not send_policemen:
                    self.log.info(f'No available units found to dispatch to intervention {id(intervention)}')

    def _dispatch_to_intervention(self, unit, intervention):
        self.log.info(f'Dispatching policeman #{id(unit)} with efficiency: {unit.efficiency} to intervention')
        self._dispatch_unit(
            unit, intervention,
            ManagementCenterNotification.DISPATCH_TO_INTERVENTION,
            ResourceState.DISPATCHED_TO_INTERVENTION,
        )

    def _dispatch_to_gunfight(self, unit, intervention):
        self.log.info(f'Dispatching policeman #{id(unit)} with efficiency: {unit.efficiency} to gunfight')
        self._dispatch_unit(
            unit, intervention,
            resource_state=ResourceState.DISPATCHED_TO_GUNFIGHT,
            notification_type=ManagementCenterNotification.DISPATCH_TO_GUNFIGHT,
        )

    def _dispatch_unit(self, unit, event, notification_type, resource_state):
        self._resource_monitor.set_unit_state(unit, resource_state, event)
        Notifications.send(
            notification_type, self,
            payload={
                'location': event.location,
                'policeman': unit
            }
        )

    def _dispatch_ambulance(self, event):
        requested_ambulance_for_event = self._resource_monitor.ambulance_requested(event)
        ambulances_available_for_event = self._resource_monitor.ambulances_available(event)
        # Omit action when ambulances are not available - response has been received
        # Or when already requested for that event
        if ambulances_available_for_event and not requested_ambulance_for_event:
            self.log.info(f'Requesting ambulance assistance for event {id(event)}')
            Notifications.send(
                ManagementCenterNotification.REQUEST_AMBULANCE_ASSISTANCE, self,
                payload={
                    'location': event.location
                }
            )
            self._resource_monitor.set_ambulance_requested(event)
