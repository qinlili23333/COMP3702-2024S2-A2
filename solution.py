import sys
import time
from constants import *
from environment import *
from state import State
"""
solution.py

This file is a template you should use to implement your solution.

You should implement each section below which contains a TODO comment.

COMP3702 2022 Assignment 2 Support Code

"""


class Solver:

    def __init__(self, environment: Environment):
        self.environment = environment
        #
        # TODO: Define any class instance variables you require (e.g. dictionary mapping state to VI value) here.
        #
        self.state={}
        self.state_cache={}

    @staticmethod
    def testcases_to_attempt():
        """
        Return a list of testcase numbers you want your solution to be evaluated for.
        """
        # TODO: modify below if desired (e.g. disable larger testcases if you're having problems with RAM usage, etc)
        return [1, 2, 3, 4, 5, 6]

    # === Value Iteration ==============================================================================================

    ### BFS mode
    def vi_initialise(self):
        """
        Initialise any variables required before the start of Value Iteration.
        """
        #
        # TODO: Implement any initialisation for Value Iteration (e.g. building a list of states) here. You should not
        #  perform value iteration in this method.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        init_state=self.environment.get_init_state()
        self.state[init_state]=0.0
        self.state_cache[init_state]=0.0
        sub_states=init_state.get_successors()
        while(len(sub_states)!=0):
            new_sub_states=[]
            for i in sub_states:
                self.state_cache[i]=0.0
                if i in self.state:
                    continue
                if i in self.environment.obstacle_map:
                    self.state[i]=-self.environment.collision_penalty
                elif i in self.environment.thorn_map:
                    self.state[i]=-self.environment.thorn_penalty
                elif self.environment.is_solved(i):
                    self.state[i]=100.0
                else:
                    self.state[i]=0.0
                new_sub_states+=i.get_successors()
            sub_states=new_sub_states


    def vi_is_converged(self):
        """
        Check if Value Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        #
        # TODO: Implement code to check if Value Iteration has reached convergence here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        delta=0.01
        converg=True
        for i in self.state_cache:
            if self.state.get(i)==None:
                self.state[i]=self.state_cache[i]
                converg=False
                pass
            if abs(self.state[i]-self.state_cache[i])>delta:
                converg=False
        return converg

    def vi_iteration(self):
        """
        Perform a single iteration of Value Iteration (i.e. loop over the state space once).
        """
        #
        # TODO: Implement code to perform a single iteration of Value Iteration here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        dis_factor=0.9
        self.state_cache=self.state.copy()
        for i in self.state:
            # calculate value
            max=-10000
            for j in BEE_ACTIONS:
                val=0
                p_double=self.environment.double_move_probs[j]
                p_double_cw=self.environment.double_move_probs[j]*self.environment.drift_cw_probs[j]
                p_double_ccw=self.environment.double_move_probs[j]*self.environment.drift_ccw_probs[j]
                p_cw=self.environment.drift_cw_probs[j]
                p_ccw=self.environment.drift_ccw_probs[j]
                p_success=1-p_double-p_cw-p_ccw-p_double_cw-p_double_ccw

                preview=self.environment.apply_dynamics(i,j)
                val+=p_success*(self.vi_get_state_value(preview[1])*dis_factor+preview[0])
                if p_double!=0:
                    val+=p_double*(self.vi_get_state_value(self.environment.apply_dynamics(preview[1],j)[1])*dis_factor+2*preview[0])
                if p_cw!=0:
                    val+=p_cw*(self.vi_get_state_value(self.environment.apply_dynamics(self.environment.apply_dynamics(i,SPIN_RIGHT)[1],j)[1])*dis_factor-ACTION_BASE_COST[SPIN_RIGHT])
                    if p_double!=0:
                        val+=p_double_cw*(self.vi_get_state_value(self.environment.apply_dynamics(self.environment.apply_dynamics(self.environment.apply_dynamics(i,SPIN_RIGHT)[1],j)[1],j)[1])*dis_factor+2*self.environment.apply_dynamics(i,SPIN_RIGHT)[0])
                if p_ccw!=0:
                    val+=p_ccw*(self.vi_get_state_value(self.environment.apply_dynamics(self.environment.apply_dynamics(i,SPIN_LEFT)[1],j)[1])*dis_factor-ACTION_BASE_COST[SPIN_LEFT])
                    if p_double!=0:
                        val+=p_double_ccw*(self.vi_get_state_value(self.environment.apply_dynamics(self.environment.apply_dynamics(self.environment.apply_dynamics(i,SPIN_LEFT)[1],j)[1],j)[1])*dis_factor+2*self.environment.apply_dynamics(i,SPIN_LEFT)[0])
                if val>max:
                    max=val
            self.state[i]=max

    def vi_plan_offline(self):
        """
        Plan using Value Iteration.
        """
        # !!! In order to ensure compatibility with tester, you should not modify this method !!!
        self.vi_initialise()
        while True:
            self.vi_iteration()

            # NOTE: vi_iteration is always called before vi_is_converged
            if self.vi_is_converged():
                break

    def vi_get_state_value(self, state: State):
        """
        Retrieve V(s) for the given state.
        :param state: the current state
        :return: V(s)
        """
        #
        # TODO: Implement code to return the value V(s) for the given state (based on your stored VI values) here. If a
        #  value for V(s) has not yet been computed, this function should return 0.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        if state in self.environment.obstacle_map:
           return -self.environment.collision_penalty
        elif state in self.environment.thorn_map:
            return -self.environment.thorn_penalty
        elif self.environment.is_solved(state):
            return 100.0
        return self.state_cache[state]

    def vi_select_action(self, state: State):
        """
        Retrieve the optimal action for the given state (based on values computed by Value Iteration).
        :param state: the current state
        :return: optimal action for the given state (element of ROBOT_ACTIONS)
        """
        #
        # TODO: Implement code to return the optimal action for the given state (based on your stored VI values) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        max=-10000
        action=FORWARD
        for i in BEE_ACTIONS:
            val=0
            p_double=self.environment.double_move_probs[i]
            p_cw=self.environment.drift_cw_probs[i]
            p_ccw=self.environment.drift_ccw_probs[i]
            p_success=1-p_double-p_cw-p_ccw

            preview=self.environment.apply_dynamics(state,i)
            val+=p_success*(self.vi_get_state_value(preview[1])*0.9+preview[0])
            if p_double!=0:
                val+=p_double*(self.vi_get_state_value(self.environment.apply_dynamics(preview[1],i)[1])*0.9+2*preview[0])
            if p_cw!=0:
                val+=p_cw*(self.vi_get_state_value(self.environment.apply_dynamics(state,SPIN_RIGHT)[1])*0.9-ACTION_BASE_COST[SPIN_RIGHT])
            if p_ccw!=0:
                val+=p_ccw*(self.vi_get_state_value(self.environment.apply_dynamics(state,SPIN_LEFT)[1])*0.9-ACTION_BASE_COST[SPIN_LEFT])
            if val>max:
                max=val
                action=i  
            #print(val) 
        #print(action)
        return action
        

    # === Policy Iteration =============================================================================================

    def pi_initialise(self):
        """
        Initialise any variables required before the start of Policy Iteration.
        """
        #
        # TODO: Implement any initialisation for Policy Iteration (e.g. building a list of states) here. You should not
        #  perform policy iteration in this method. You should assume an initial policy of always move FORWARDS.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        init_state=self.environment.get_init_state()
        self.state[init_state]=0.0
        self.state_cache[init_state]=0.0
        sub_states=init_state.get_successors()
        while(len(sub_states)!=0):
            new_sub_states=[]
            for i in sub_states:
                self.state_cache[i]=0.0
                if i in self.state:
                    continue
                if i in self.environment.obstacle_map:
                    self.state[i]=-self.environment.collision_penalty
                elif i in self.environment.thorn_map:
                    self.state[i]=-self.environment.thorn_penalty
                elif self.environment.is_solved(i):
                    self.state[i]=100.0
                else:
                    self.state[i]=0.0
                new_sub_states+=i.get_successors()
            sub_states=new_sub_states

    def pi_is_converged(self):
        """
        Check if Policy Iteration has reached convergence.
        :return: True if converged, False otherwise
        """
        #
        # TODO: Implement code to check if Policy Iteration has reached convergence here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def pi_iteration(self):
        """
        Perform a single iteration of Policy Iteration (i.e. perform one step of policy evaluation and one step of
        policy improvement).
        """
        #
        # TODO: Implement code to perform a single iteration of Policy Iteration (evaluation + improvement) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    def pi_plan_offline(self):
        """
        Plan using Policy Iteration.
        """
        # !!! In order to ensure compatibility with tester, you should not modify this method !!!
        self.pi_initialise()
        while True:
            self.pi_iteration()

            # NOTE: pi_iteration is always called before pi_is_converged
            if self.pi_is_converged():
                break

    def pi_select_action(self, state: State):
        """
        Retrieve the optimal action for the given state (based on values computed by Value Iteration).
        :param state: the current state
        :return: optimal action for the given state (element of ROBOT_ACTIONS)
        """
        #
        # TODO: Implement code to return the optimal action for the given state (based on your stored PI policy) here.
        #
        # In order to ensure compatibility with tester, you should avoid adding additional arguments to this function.
        #
        pass

    # === Helper Methods ===============================================================================================
    #
    #
    # TODO: Add any additional methods here
    #
    #

