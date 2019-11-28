#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 11:02:21 2019

@author: HRI Group4
"""

import cozmo
import asyncio
import time
import math
from cozmo.util import degrees, distance_mm, speed_mmps, Pose
from cozmo.objects import CustomObject, CustomObjectMarkers, CustomObjectTypes

actions_list = []
cubes = []

def handle_object_appeared(evt, **kw):
    # This will be called whenever an EvtObjectAppeared is dispatched -
    # whenever an Object comes into view.
    global actions_list
    if isinstance(evt.obj, CustomObject):
        print("Cozmo started seeing a %s" % str(evt.obj.object_type))
        actions_list.append(evt.obj.object_type)


def handle_object_disappeared(evt, **kw):
    # This will be called whenever an EvtObjectDisappeared is dispatched -
    # whenever an Object goes out of view.
    if isinstance(evt.obj, CustomObject):
        print("Cozmo stopped seeing a %s" % str(evt.obj.object_type))
        
        
def custom_objects(robot):
    #----------------- DEFINE ALL THE MARKERS -----------------#
	# Detect Cube		->	circles2
	# Approach Cube	->	circles3
	# Raise Forklift		->	circles4
	# Lower Forklift		->	circles5
	# Turn Left			->	diamonds2
	# Turn Right			->	diamonds3
	# Move Forward		->	diamonds4
	# Move Backward	->	diamonds5
	# Execution Card	->	hexagons2
	circles2 = robot.world.define_custom_cube(CustomObjectTypes.CustomType01,CustomObjectMarkers.Circles2,55,50, 50, True)
	circles3 = robot.world.define_custom_cube(CustomObjectTypes.CustomType02,CustomObjectMarkers.Circles3,55,50, 50, True)
	circles4 = robot.world.define_custom_cube(CustomObjectTypes.CustomType03,CustomObjectMarkers.Circles4,55,50, 50, True)
	circles5 = robot.world.define_custom_cube(CustomObjectTypes.CustomType04,CustomObjectMarkers.Circles5,55,50, 50, True)
	diamonds2 = robot.world.define_custom_cube(CustomObjectTypes.CustomType05,CustomObjectMarkers.Diamonds2,55,50, 50, True)
	diamonds3= robot.world.define_custom_cube(CustomObjectTypes.CustomType06,CustomObjectMarkers.Diamonds3,55,50, 50, True)
	diamonds4 = robot.world.define_custom_cube(CustomObjectTypes.CustomType07,CustomObjectMarkers.Diamonds4,55,50, 50, True)
	diamonds5 = robot.world.define_custom_cube(CustomObjectTypes.CustomType08,CustomObjectMarkers.Diamonds5,55,50, 50, True)
	hexagons2 = robot.world.define_custom_cube(CustomObjectTypes.CustomType09,CustomObjectMarkers.Hexagons2,55,50, 50, True)

# Create a "map" of the game board - Store the cubes location
def store_2_cube_locations(robot):
    global cubes, targ, stack
    lookaround = robot.start_behavior(cozmo.behavior.BehaviorTypes.LookAroundInPlace)
    cubes = robot.world.wait_until_observe_num_objects(num=2, object_type=cozmo.objects.LightCube, timeout=60)
    lookaround.stop()
    if len(cubes) != 2:
        return 1
    else:
        return 0

# Approach and dock a cube that is in a known location
def approach_cube(robot, cube):
    print(cube)
    action = robot.dock_with_cube(cube, approach_angle=cozmo.util.degrees(0), num_retries=2)
    action.wait_for_completed()
    print("result:", action.result)
    return action
    
def game_start(robot):
    findface = robot.start_behavior(cozmo.behavior.BehaviorTypes.FindFaces)
    face = robot.world.wait_for_observed_face(timeout=30)
    findface.stop()
    robot.turn_towards_face(face).wait_for_completed()
    print("Start.")
    action = robot.set_lift_height(0, accel=5.0, max_speed=8.0)
    action.wait_for_completed()
    robot.say_text("Hello. I'm Paul! I'm very happy that you will play with me, but first, let me introduce the rules of this game.").wait_for_completed()
    robot.say_text("You will guide me to pick these two cubes to the goal area behind the line by using the marker cards you have.").wait_for_completed()
    robot.say_text("You have to show the cards in 60 seconds to create the sequence I will follow. And please use execution card for ending.").wait_for_completed()
    robot.say_text("Now let's play the game.").wait_for_completed()

# Get the sequence that the player shows to the robot at the beggining of the game
def get_sequence(robot):
	# Add event handlers for whenever Cozmo sees a new object
    print("Show cards.")
    robot.say_text("Please show me all the cards in sequence.").wait_for_completed()
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
    l = 0
    while True:
        if CustomObjectTypes.CustomType09 in actions_list:
            break
        robot.add_event_handler(cozmo.objects.EvtObjectAppeared, handle_object_appeared)
        robot.add_event_handler(cozmo.objects.EvtObjectDisappeared, handle_object_disappeared)
        if l+1 == len(actions_list):
            robot.say_text("Got it.").wait_for_completed()
            l = len(actions_list)
 
# Read the sequence and execute it. 
def game_logic(robot):
    global actions_list, cubes
    fail_key = suc1_key = suc2_key = 0
    tar1 = 0
    tar2 = 0
    for action in actions_list:
        if action.name == 'CustomType01':
            fail_key = store_2_cube_locations(robot)
        elif action.name == 'CustomType02':
            if tar1 == 0 and tar2 == 0:
                action = approach_cube(robot,cubes[0])
                if action.result.id == 0:
                    tar1 = 1
            else:
                action = approach_cube(robot,cubes[1])
                if action.result.id == 0:
                    tar2 = 1
        elif action.name == 'CustomType03':
            action = robot.set_lift_height(1, accel=5.0, max_speed=8.0)
            action.wait_for_completed()
            print(action.result)
        elif action.name == 'CustomType04':
            action = robot.set_lift_height(0, accel=5.0, max_speed=8.0)
            action.wait_for_completed()
            if tar1 == 1 and tar2 == 0:
                if action.result.id == 0:
                    suc1_key = 1
            else: 
                if action.result.id == 0:
                    suc2_key = 1
        elif action.name == 'CustomType05':
            robot.turn_in_place(degrees(90)).wait_for_completed()
        elif action.name == 'CustomType06':
            robot.turn_in_place(degrees(-90)).wait_for_completed()
        elif action.name == 'CustomType07':
            robot.drive_straight(distance_mm(100), speed_mmps(50)).wait_for_completed()
        elif action.name == 'CustomType08':
            robot.drive_straight(distance_mm(-100), speed_mmps(50)).wait_for_completed()
        elif action.name == 'CustomType09':
            if not fail_key and suc1_key and suc2_key:
                print("Congratulation!")
                robot.say_text("Congratulation!").wait_for_completed()
                return 1    
            else:
                actions_list = []
                action = robot.set_lift_height(0, accel=5.0, max_speed=8.0)
                action.wait_for_completed()
                print("Thank you for playing! I really hope you will try again.")
                robot.say_text("Please try again.").wait_for_completed()
                return 0
                

def run(robot: cozmo.robot.Robot):
    success = 0
    custom_objects(robot)
    game_start(robot)
    while not success:
        get_sequence(robot)
        success = game_logic(robot) 
    
if __name__ == '__main__':
    cozmo.run_program(run, use_viewer=True)