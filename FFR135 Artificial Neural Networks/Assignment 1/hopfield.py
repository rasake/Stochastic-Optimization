# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 12:23:28 2016

@author: Rasmus
"""
import numpy as np
import scipy.special

def logistic_function(x, beta):
    return scipy.special.expit(2*x*beta)
    

class HopfieldNetwork:
    def __init__(self, nbr_of_cells, initial_pattern = None, initial_weights = None):
        if initial_pattern is None:
            initial_pattern = np.ones([nbr_of_cells, 1])
        if initial_weights is None:
            initial_weights = np.zeros([nbr_of_cells, nbr_of_cells])
        self._NBR_OF_CELLS = nbr_of_cells
        self.neuron_state_vector = initial_pattern
        self.weights = initial_weights
        self._updates_since_last_reset = 0
        self._pseudo_stable_bits = np.zeros([nbr_of_cells, 1])

    @property
    def neuron_state_vector(self):
        return np.copy(self._neuron_state_vector)

    @neuron_state_vector.setter
    def neuron_state_vector(self, pattern_vector):
        if len(pattern_vector) != self._NBR_OF_CELLS:
            raise ValueError("Size of Neural Network cannot change")
        self._neuron_state_vector = np.copy(pattern_vector)


    def set_neuron(self,index, value):
        if (value != 1 and value != -1):
            message = ("Cannot set neuron " + str(index) + " to " + str(value)
                        + ", neuron states must be either +1 or -1.")
            raise ValueError(message)
        if index < 0:
            raise ValueError("Index must be positive")
        if (index > self._NBR_OF_CELLS - 1):
            message = ("Cannot set neuron, index " + str(index) + " out of bounds "
                        + "for Hopfield Network with size " + str(self._NBR_OF_CELLS)  )
            raise IndexError(message)
        self._neuron_state_vector[index] = value
            
    @property
    def weights(self):
        return self._weights

    @weights.setter
    def weights(self, new_weights):
        if np.shape(new_weights) != (self._NBR_OF_CELLS, self._NBR_OF_CELLS):
            raise ValueError("Weight matrix cannot change size")
        self._weights = np.copy(new_weights)   

    
    def feed_pattern(self, pattern_vector):
        self.neuron_state_vector = np.copy(pattern_vector)
        self._updates_since_last_reset = 0

               
    def store_pattern(self, pattern_vector):
        if len(pattern_vector) != self._NBR_OF_CELLS:
            raise ValueError("Pattern length must match number of neurons")
        temp_weights = pattern_vector @ np.transpose(pattern_vector) / self._NBR_OF_CELLS
        np.fill_diagonal(temp_weights,0)    
        self.weights += temp_weights


    def update_state(self, synchronous = True, stochastic = False, beta = 0):
        if synchronous and stochastic:
            raise ValueError("Stochastic updating cannot be synchronized," +
                "please set synchronous kwarg to False to allow stochastic updating")
        if synchronous: #Synchronous updating, all bits updated at once in parallell
            new_state = np.sign(self._weights @ self._neuron_state_vector)
            is_done = np.array_equal(self.neuron_state_vector, new_state)
            self.neuron_state_vector = new_state
        else: #Asynchronous updating, only one bit will change
            index = np.random.randint(0, self._NBR_OF_CELLS) #Start inclusive, stop exclusive
            local_field = (self.weights[index] @ self.neuron_state_vector ) [0]

            if stochastic:
                if np.random.rand() < logistic_function(local_field, beta):
                    new_neuron_value = 1
                else:
                    new_neuron_value = -1
            else: #deterministic
                new_neuron_value = np.sign(local_field)
            is_flipped = (new_neuron_value != self.neuron_state_vector[index])
            if is_flipped:
                self._pseudo_stable_bits = 0 * self._pseudo_stable_bits
            else:
                self._pseudo_stable_bits[index] = 1
            is_done = np.all(self._pseudo_stable_bits)
            self.set_neuron(index, new_neuron_value)           
        self._updates_since_last_reset +=1
        return is_done
    
    def run_until_convergence(self, synchronous = True):
        is_done = False
        while not is_done:
            is_done = self.update_state(synchronous=synchronous)
        return self.neuron_state_vector, self._updates_since_last_reset
            
