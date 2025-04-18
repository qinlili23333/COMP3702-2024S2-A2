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
        self.policy={}
        self.policy_cache={}

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
        delta=0.001
        converg=True
        for i in self.state_cache:
            if self.state.get(i)==None:
                self.state[i]=self.state_cache[i]
                converg=False
                pass
            if abs(self.state[i]-self.state_cache[i])>delta:
                converg=False
        #x=[self.state[i] for i in self.state_cache]
        #print(max(x),min(x))
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
        dis_factor=0.98
        self.state_cache=self.state.copy()
        for i in self.state:
            # calculate value
            maxv=-10000
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
                    p2=self.environment.apply_dynamics(preview[1],j)
                    val+=p_double*(self.vi_get_state_value(self.environment.apply_dynamics(preview[1],j)[1])*dis_factor+min(preview[0],p2[0]))
                if p_cw!=0:
                    p1=self.environment.apply_dynamics(i,SPIN_RIGHT)
                    p2=self.environment.apply_dynamics(p1[1],j)
                    val+=p_cw*(self.vi_get_state_value(p2[1])*dis_factor+min(p1[0],p2[0]))
                    if p_double!=0:
                        p3=self.environment.apply_dynamics(p2[1],j)
                        val+=p_double_cw*(self.vi_get_state_value(p3[1])*dis_factor+min(p1[0],p2[0],p3[0]))
                if p_ccw!=0:
                    p1=self.environment.apply_dynamics(i,SPIN_LEFT)
                    p2=self.environment.apply_dynamics(p1[1],j)
                    val+=p_ccw*(self.vi_get_state_value(p2[1])*dis_factor+min(p1[0],p2[0]))
                    if p_double!=0:
                        p3=self.environment.apply_dynamics(p2[1],j)
                        val+=p_double_ccw*(self.vi_get_state_value(p3[1])*dis_factor+min(p1[0],p2[0],p3[0]))
                if val>maxv:
                    maxv=val
            self.state[i]=maxv

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
        maxv=-10000
        action=FORWARD
        dis_factor=0.98
        i=state
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
                p2=self.environment.apply_dynamics(preview[1],j)
                val+=p_double*(self.vi_get_state_value(self.environment.apply_dynamics(preview[1],j)[1])*dis_factor+min(preview[0],p2[0]))
            if p_cw!=0:
                p1=self.environment.apply_dynamics(i,SPIN_RIGHT)
                p2=self.environment.apply_dynamics(p1[1],j)
                val+=p_cw*(self.vi_get_state_value(p2[1])*dis_factor+min(p1[0],p2[0]))
                if p_double!=0:
                    p3=self.environment.apply_dynamics(p2[1],j)
                    val+=p_double_cw*(self.vi_get_state_value(p3[1])*dis_factor+min(p1[0],p2[0],p3[0]))
            if p_ccw!=0:
                p1=self.environment.apply_dynamics(i,SPIN_LEFT)
                p2=self.environment.apply_dynamics(p1[1],j)
                val+=p_ccw*(self.vi_get_state_value(p2[1])*dis_factor+min(p1[0],p2[0]))
                if p_double!=0:
                    p3=self.environment.apply_dynamics(p2[1],j)
                    val+=p_double_ccw*(self.vi_get_state_value(p3[1])*dis_factor+min(p1[0],p2[0],p3[0]))
            if val>maxv:
                maxv=val
                action=j
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
        self.policy[init_state]=FORWARD
        self.policy_cache[init_state]=REVERSE
        sub_states=init_state.get_successors()
        while(len(sub_states)!=0):
            new_sub_states=[]
            for i in sub_states:
                self.policy[i]=FORWARD
                self.policy_cache[i]=REVERSE
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
        converged=True
        for i in self.policy_cache:
            if self.policy[i]!=self.policy_cache[i]:
                converged=False
        return converged


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
        """
        Some code are copied and modified from solution of tutorial 7
        """
        self.policy_evaluation()
        self.policy_improvement()


    def policy_evaluation(self):
        # Use iterative / naive solution for policy evaluation
        """
        Perform a single iteration of Policy Evaluation to convergence
        """

        values_converged = False
        dis_factor = 0.98
        delta=1
        while not values_converged:
            self.state_cache=self.state.copy()
            for i in self.state:
                # calculate value
                j=self.policy[i]
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
                    p2=self.environment.apply_dynamics(preview[1],j)
                    val+=p_double*(self.vi_get_state_value(self.environment.apply_dynamics(preview[1],j)[1])*dis_factor+min(preview[0],p2[0]))
                if p_cw!=0:
                    p1=self.environment.apply_dynamics(i,SPIN_RIGHT)
                    p2=self.environment.apply_dynamics(p1[1],j)
                    val+=p_cw*(self.vi_get_state_value(p2[1])*dis_factor+min(p1[0],p2[0]))
                    if p_double!=0:
                        p3=self.environment.apply_dynamics(p2[1],j)
                        val+=p_double_cw*(self.vi_get_state_value(p3[1])*dis_factor+min(p1[0],p2[0],p3[0]))
                if p_ccw!=0:
                    p1=self.environment.apply_dynamics(i,SPIN_LEFT)
                    p2=self.environment.apply_dynamics(p1[1],j)
                    val+=p_ccw*(self.vi_get_state_value(p2[1])*dis_factor+min(p1[0],p2[0]))
                    if p_double!=0:
                        p3=self.environment.apply_dynamics(p2[1],j)
                        val+=p_double_ccw*(self.vi_get_state_value(p3[1])*dis_factor+min(p1[0],p2[0],p3[0]))
                self.state[i]=val
            # check convergence
            differences = [abs(self.state_cache[s] - self.state[s]) for s in self.state]
            if max(differences) < delta:
                values_converged = True


    def policy_improvement(self):
        policy_changed = False
        self.policy_cache=self.policy.copy()
        # loop over each state, and improve the policy using 1-step lookahead and the values from policy_evaluation
        for s in self.state:
            self.policy[s]=self.vi_select_action(s)

        self.converged = not policy_changed

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
        return self.policy[state]

    # === Helper Methods ===============================================================================================
    #
    #
    # TODO: Add any additional methods here
    #
    #

