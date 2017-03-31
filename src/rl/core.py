"""Core classes."""
from operator import itemgetter
import matplotlib.pyplot as plt
import numpy as np



class Sample:
    """Represents a reinforcement learning sample.

    Used to store observed experience from an MDP. Represents a
    standard `(s, a, r, s', terminal)` tuple.

    Note: This is not the most efficient way to store things in the
    replay memory, but it is a convenient class to work with when
    sampling batches, or saving and loading samples while debugging.

    Parameters
    ----------
    state: array-like
      Represents the state of the MDP before taking an action. In most
      cases this will be a numpy array. Dimensions: (w, h, nframe)
    action: int, float, tuple
      For discrete action domains this will be an integer. For
      continuous action domains this will be a floating point
      number. For a parameterized action MDP this will be a tuple
      containing the action and its associated parameters.
    reward: float
      The reward received for executing the given action in the given
      state and transitioning to the resulting state.
    next_state: array-like
      This is the state the agent transitions to after executing the
      `action` in `state`. Expected to be the same type/dimensions as
      the state.
    is_terminal: boolean
      True if this action finished the episode. False otherwise.
    """
    def __init__(self, s, a, r, s_p, is_terminal):
        self._s = s;
        self._a = a;
        self._r = r;
        self._s_p = s_p;
        self._is_terminal = is_terminal;
        
    @property
    def s(self):
        return self._s;

    @property
    def a(self):
        return self._a;
    
    @property
    def r(self):
        return self._r;
    
    @property
    def s_p(self):
        return self._s_p;
    
    @property
    def is_terminal(self):
        return self._is_terminal;
    
    @property
    def id(self):
        return self._id;
    
    def __str__(self):
        return (str(self.s) + ',' + str(self.a) 
                + ',' + str(self.r) + ',' 
                + str(self.s_p) + ',' 
                + str(self.is_terminal));
    
    def __repr__(self):
        return (str(self.s) + ',' + str(self.a) 
                + ',' + str(self.r) + ',' 
                + str(self.s_p) + ',' 
                + str(self.is_terminal));
                
class Preprocessor:
    """Preprocessor base class.

    Preprocessor can be used to perform some fixed operations on the
    raw state from an environment. 

    Preprocessors are implemented as class so that they can have
    internal state. 

    """
    
    def __init__(self):
        """
        Constructor.
        """
    
    def process_observation(self, time, observation):
        """Preprocess the given time and observation to corresponding state.
        1. If occupant_num is 0, the PMV will be setted as 0

        Should be callled just after obtain return from environment

        Parameters
        ----------
        time: string 
            Current simulation time counting in seconds 

        observation: array of float
            Important parameters from an environment.
            Parameters are:
             [Site Outdoor Air Drybulb Temperature (C), 
             Site Outdoor Air Relative Humidity (%), 
             Site Wind Speed (m/s), Site Wind Direction (degree from north), 
             Site Diffuse Solar Radiation Rate per Area (W/m2), 
             Site Direct Solar Radiation Rate per Area (W/m2), 
             Zone Air Temperature (C), Zone Air Relative Humidity (%), 
             Zone Thermostat Heating Setpoint Temperature (C), 
             Zone Thermostat Cooling Setpoint Temperature (C), 
             Zone Thermal Comfort Fanger Model PMV, Zone People Occupant Count, 
             Facility Total HVAC Electric Demand Power (W)]

        
        Returns
        -------
        state_raw: list of float
            Current state
         
        setpoint_this: list of float
           Current heating and cooling setpoint

        reward: float

        """
        Occupant_num = observation[-2]
        if (Occupant_num == 0):
            observation[10] = 0 
        state_raw = observation[0:11] + [observation[-1]]
        setpoint_this = observation[8:10]
        reward = observation[10]
        return state_raw, setpoint_this, reward


    def process_state_for_network(self, state, memories):
        """Preprocess the given time and observation to corresponding state 
        before giving it to the network.

        Should be called just before the action is selected.

        This is a different method from the process_state_for_memory
        because the replay memory may require a different storage
        format to reduce memory usage. For example, storing images as
        uint8 in memory is a lot more efficient thant float32, but the
        networks work better with floating point images.

        Parameters
        ----------
        state: np.ndarray
          Generally a numpy array. A single state from an environment.
          

        Returns
        -------
        processed_state: np.ndarray of float
          Generally a numpy array. The state after processing. 

        """
        #do gray scale: https://en.wikipedia.org/wiki/Grayscale

        gray_frame = (0.2126 * state[:,:,0] + 0.7152 * state[:,:,1] 
                      + 0.0722 * state[:,:,2]);
        
        #down sampling
        gray_frame_down = imresize(gray_frame, DOWN_SIZE_DIM)/255.0;
        
        #crop
        gray_frame_down = gray_frame_down[0:self._crop_x, 0:self._crop_y];
        
        return gray_frame_down;

    def process_state_for_memory(self, state):
        """Preprocess the given state before giving it to the replay memory.

        Should be called just before appending this to the replay memory.

        This is a different method from the process_state_for_network
        because the replay memory may require a different storage
        format to reduce memory usage. For example, storing images as
        uint8 in memory and the network expecting images in floating
        point.

        Parameters
        ----------
        state: array
          A single state from an environmnet. .

        Returns
        -------
        processed_state: np.ndarray of uint8. 
          Generally a numpy array. The state after processing. 

        """
  
        state_unit8 = np.array(state).astype('uint16');
        

        return state_unit8;


    def process_batch(self, samples):
        """Process batch of samples.

        If your replay memory storage format is different than your
        network input, you may want to apply this function to your
        sampled batch before running it through your update function.

        Parameters
        ----------
        samples: list(tensorflow_rl.core.Sample)
          List of samples to process

        Returns
        -------
        processed_samples: list(tensorflow_rl.core.Sample)
          Samples after processing. Can be modified in anyways, but
          the list length will generally stay the same.
        """
        list_samples = [];
        
        for sample in samples:
            s = sample.s;
            s_p = sample.s_p;
            
            assert (s.dtype is np.dtype('uint8'));
            assert (s_p.dtype is np.dtype('uint8'))
            
            r = sample.r;
            a = sample.a;
            is_terminal = sample.is_terminal;
            
            #process, change the s and s_p in list of int 0~255 to list
            #of float 0~1.
            s = s/255.0;
            s_p = s_p/255.0;
            
            #Add a new dimension to match the tensor dimension
            #s = s.reshape((1,) + s.shape);
            #s_p = s_p.reshape((1,) + s_p.shape);
            
            list_samples.append(Sample(s, a, r, s_p, is_terminal));
            
        return list_samples;

    def process_reward(self, reward):
        """Process the reward.

        Useful for things like reward clipping. The Atari environments
        from DQN paper do this. Instead of taking real score, they
        take the sign of the delta of the score.

        Parameters
        ----------
        reward: float
          Reward to process

        Returns
        -------
        processed_reward: float
          The processed reward
        """
        if reward > 0:
            return 1;
        else:
            return 0;

    def reset(self):
        """Reset any internal state.

        Will be called at the start of every new episode. Makes it
        possible to do history snapshots.
        """
        #may not be applicable
        pass


class ReplayMemory:
    """Interface for replay memories.

    We have found this to be a useful interface for the replay
    memory. Feel free to add, modify or delete methods/attributes to
    this class.

    It is expected that the replay memory has implemented the
    __iter__, __getitem__, and __len__ methods.

    If you are storing raw Sample objects in your memory, then you may
    not need the end_episode method, and you may want to tweak the
    append method. This will make the sample method easy to implement
    (just ranomly draw saamples saved in your memory).

    However, the above approach will waste a lot of memory (as states
    will be stored multiple times in s as next state and then s' as
    state, etc.). Depending on your machine resources you may want to
    implement a version that stores samples in a more memory efficient
    manner.

    Methods
    -------
    append(state_this, state_next, action, reward, debug_info=None)
      
    end_episode(final_state, is_terminal, debug_info=None)
      Set the final state of an episode and mark whether it was a true
      terminal state (i.e. the env returned is_terminal=True), of it
      is is an artificial terminal state (i.e. agent quit the episode
      early, but agent could have kept running episode).
    sample(batch_size, indexes=None)
      Return list of samples from the memory. Each class will
      implement a different method of choosing the
      samples. Optionally, specify the sample indexes manually.
    clear()
      Reset the memory. Deletes all references to the samples.
    """
    def __init__(self, max_size):
        """Setup memory.

        You should specify the maximum size o the memory. Once the
        memory fills up oldest values should be removed. You can try
        the collections.deque class as the underlying storage, but
        your sample method will be very slow.

        We recommend using a list as a ring buffer. Just track the
        index where the next sample should be inserted in the list.
        """
        self._max_size = max_size;
        self._stateRingList = [None for _ in range(max_size)];
        self._pointer = 0;
        self._real_time_state_len = 0;
        self._i = 0;
        
        #rinf buf is [s,a,r,s',a',r',s'',a'',r'',s''',.....]

    def append(self, sample):
        """
        Add a sample to the replay memory. The sample can be any python
        object, but it is suggested that tensorflow_rl.core.Sample be
        used.
        
        Arguments:
            sample: Sample object 
        """
        self._stateRingList[self._pointer] = sample;
        self._pointer_incre();
    
    def end_episode(self, final_state, is_terminal):
        #raise NotImplementedError('This method should be overridden')
        pass;
        
    def sample(self, batch_size, indexes=None):
        
        totalChoice = np.array(range(self._real_time_state_len));
        sampled_idxs = np.random.choice(totalChoice
                                            , batch_size
                                            , replace = False).tolist();
        return itemgetter(*sampled_idxs)(self._stateRingList);
    
    def __len__(self):
        return self._real_time_state_len;
    
    def __iter__(self):
        return self;
    
    def __next__(self):
        if self._i < self._real_time_state_len:
            i = self._i;
            self._i += 1;
            return self._stateRingList[i];
        else:
            self._i = 0;
            raise StopIteration();
    
    def __getitem__(self, i):
        return self._stateRingList[i];
    
    def _pointer_incre(self):
        self._pointer = (self._pointer + 1) % self._max_size;
        self._real_time_state_len = min(self._real_time_state_len+1
                                     , self._max_size);
