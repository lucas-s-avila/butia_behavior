#!/usr/bin/env python
import rospy
import smach
import operator

from butia_behavior.machines.classes_count import getClassesCountMachine
from butia_behavior.states import SaySomethingUDState, PrepareSpeechState

def average(counts):
  return reduce(operator.add, counts) / len(counts)

if __name__ == '__main__':
  rospy.init_node('object_counter')
  sm = smach.StateMachine(outcomes=['succeeded', 'aborted', 'preempted'])
  with sm:
    sm1 = getWaitDoorMachine()
    smach.StateMachine.add('WAIT_DOOR', sm1, transitions={
      'succeeded': 'GOTO_1',
      'error': 'aborted',
    })
    sm2 = getGoToFixedMachine('shelf')
    smach.StateMachine.add('GOTO_1', sm2, transitions={
      'succeeded': 'COUNT_OBJECTS',
      'aborted': 'aborted',
      'preempted': 'preempted'
    })
    sm3 = getClassesCountMachine('butia_vision/or/people_detection', 20, max)
    smach.StateMachine.add(
      'COUNT_OBJECTS',
      sm3,
      transitions={
        'succeeded': 'PREPARE_SPEECH',
        'error': 'aborted'
      }
    )
    smach.StateMachine.add(
      'PREPARE_SPEECH',
      PrepareSpeechState('I identified','{y} {x}', 'in the room'),
      transitions={
        'succeeded': 'SAY_SOMETHING',
        'error': 'aborted'
      },
      remapping={
        'registers': 'registers'
      }
    )
    smach.StateMachine.add(
      'SAY_SOMETHING',
      SaySomethingUDState(),
      transitions={
        'succeeded': 'GOTO_2',
        'error': 'GOTO_2'
      }
    )
    sm4 = getGoToFixedMachine('exit')
    smach.StateMachine.add('GOTO_2', sm4, transitions={
      'succeeded': 'succeeded',
      'aborted': 'aborted',
      'preempted': 'preempted'
    })
  outcome = sm.execute()
