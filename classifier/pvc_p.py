import tensorflow as tf
import datetime
import scipy as sci

#############################################################
###                    #CalCardiac                        ###
#############################################################

class pvc_p(object):

    def __init__(self, N, T, C):
        # Data Inputs and Parameters
        self.num_mini_batch = N # Mini-batch size
        self.num_samples = T # Number of samples/dimension of input space
        self.num_channels = C    # Number of channels
        
        self.input_shape = [self.num_mini_batch,
                            self.num_samples,
                            self.num_channels]
        
        self.X_in = tf.placeholder(dtype=tf.float32, shape=self.input_shape)
        self.y_in = tf.placeholder(dtype=tf.float32, shape=[self.input_shape[0], 1])
        
        # Model Hyperparameters and Convenience Quantities
        self.learning_rate = 1.0
        self.regularization_rate = 1.0
        self.param_std_dev = 1.0

        self.layer_1_filter_width = 3
        self.layer_1_num_filters = 10
        self.layer_1_input_channels = 1
        
        self.layer_1_shape = [self.layer_1_filter_width,    # Filter width 
                              self.layer_1_input_channels,  # Input channels
                              self.layer_1_num_filters]     # Output channels

        self.layer_1_output_size = (self.num_samples - self.layer_1_filter_width + 1)
        self.layer_1_output_reshape_size = (self.num_samples - self.layer_1_filter_width + 1) * self.layer_1_num_filters        
        self.layer_1_bias_shape = [1,                       # Same for all sample points, broadcast in this dimension
                                   self.layer_1_output_size,
                                   self.layer_1_num_filters]

        self.network_output_size = 1
        self.layer_2_shape = [self.layer_1_output_reshape_size, self.network_output_size]
        self.layer_2_bias_shape = [self.network_output_size]        


        
        # Model Parameters/Decision Variables
        self.layer_1_filters = tf.Variable(tf.random_normal(shape=self.layer_1_shape, mean=0, stddev=self.param_std_dev,
                                                            dtype=tf.float32), dtype=tf.float32)
        self.layer_1_bias = tf.Variable(tf.zeros(shape=self.layer_1_bias_shape, dtype=tf.float32), dtype=tf.float32)
        
        self.layer_2_fc = tf.Variable(tf.random_normal(shape=self.layer_2_shape,
                                                       mean=0, stddev = self.param_std_dev,
                                                       dtype=tf.float32), dtype=tf.float32)
        self.layer_2_bias = tf.Variable(tf.zeros(shape=self.layer_2_bias_shape))
        
        # Forward pass
        self.X_1 = tf.reshape(tf.nn.conv1d(value=self.X_in,
                                           filters=self.layer_1_filters,
                                           stride=1,
                                           padding='VALID') + self.layer_1_bias,
                              [self.num_mini_batch, self.layer_1_output_reshape_size])

        self.pvc_logits = tf.matmul(self.X_1, self.layer_2_fc) + self.layer_2_bias
        self.pvc_dobs = tf.sigmoid(self.pvc_logits)

        # Error measure
        self.error = (1/self.num_mini_batch)*(self.learning_rate*tf.reduce_sum(
            tf.nn.sigmoid_cross_entropy_with_logits(labels=self.y_in,
                                                    logits=self.pvc_logits)) + 
            self.regularization_rate*(tf.reduce_sum(tf.square(self.layer_1_filters)) +
                                    tf.reduce_sum(tf.square(self.layer_1_filters))))
            
        # Gradient update
        self.opt = tf.train.GradientDescentOptimizer(self.learning_rate)
        self.grad = self.opt.compute_gradients(self.error)
        self.train_step = self.opt.apply_gradients(self.grad)
        
        # Session and Initialization
        self.sess = tf.Session()
        self.init = tf.global_variables_initializer()
        self.sess.run(self.init) # Initial initialization

        # Save/Load
        self.model_dir = 'tf_saved_models/'
        self.saver = tf.train.Saver()

    # param X: input values (ecg sequences)
    def predict(self, X, thresh = 0.5):
        return self.sess.run(self.pvc_dobs, feed_dict={self.X_in: X}) > thresh

    # param n: number of training steps
    # param data_gen_iterable
    def train_n_steps(self, n, data_gen_iterable):
        training_error = []
        validation_error = []
        for (train_batch, validation_batch) in data_gen():
            E_train = self.sgd_update(train_batch[0], train_batch[1])
            E_val = self.get_error(validation_batch[0], validation_batch[1])

            training_error.append(E_train)
            validation_error.append(E_val)
        return training_error, validation_error

    # Performs a single training step based on X and y
    def sgd_update(self, X_instance, y_instance):
        E,_ = self.sess.run([self.error, self.train_step], feed_dict={X_in: X_instance, y_in: y_instance})
        return E

    # just returns error without update
    def get_error(self, X_instance, y_instance):
        E = self.sess.run(self.error, feed_dict={X_in: X_instance, y_in: y_instance})
        return E
    
    def reinitialize_sess(self):
        selection = input('Current session will be lost. Save first? (y/n)')
        if selection == 'y':
            self.save_session()
        elif selection == 'n':
            print('New session initialized.')
            self.sess.run(self.init)

    def save_session(self, out_filename):
        self.saver.save(self.sess,
                        self.model_dir + out_filename + '_' + str(datetime.datetime.now()).replace(' ', '_'))
        
    def load_session(self, in_filename):
        self.saver.restore(self.sess,
                           self.model_dir + in_filename)

    def test(self, N, T, C):
        X = sci.random.rand(N, T).reshape([N, T, C])
        print(self.predict(X))

###############################################################
###                     Data                                ###
###############################################################

class data_gen:
    def __init__(self):
        pass
    
    def __iter__(self):
        pass
    
    def __next__(self, n):
        pass

    
def main():
    import os
    # Documentation
    print('Training REPL for CalCardiac PVC classifier')
    __doc__ = """
Available Commands:
    get:
        help:    show this help documentation
        status:  show status of tensorflow model
        param:   show parameters of tf model

    set:     
        param:   set hyperparameters of tf model
        init:    initialize or reinitialize session (loss warning)
        data:    

    save:        save current session

    load:        load session from file

    test:        run some unit tests
         
    exit:        exit

        For example: type 'get param' to display current hyperparameters
 """
    print(__doc__)
    
    # Components
    N = 10
    T = 2400   
    C = 1
    aa = pvc_p(N, T, C)
    
    while True: # Looop
        # Read
        selection = input('CalCardiac>>> ')
        # Eval & Print
        if selection.strip()[0] == 'get':       
            if selection.strip()[1].startswith('help'):
                print(__doc__)
                        
            elif selection.strip()[1].startswith('status'):
                print('not yet implemented')

            elif selection.strip()[1].startswith('param'):
                print('learning rate: ' + str(aa.learning_rate))
                print('regularization rate: ' + str(aa.regularization_rate))
                print('parameter std dev:' + str(aa.param_std_dev))
                
        elif selection.strip()[0].startswith('set'):
            if selection.strip()[1].startswith('param'):
                print('not yet implemented')
                
        elif selection.startswith('save'):
            out_filename = input('TensorFlow session output filename: ')
            if os.path.isfile(out_filename):
                overwrite = input('Overwrite file? (y/n)')
            if overwrite == 'y':
                aa.save_session(out_filename)
                        
        elif selection.startswith('load'):
            in_filename = input('TensorFlow session input filename: ')
            try:
                aa.load_session(in_filename)
            except:
                print('Session failed to load. File not found.')

        elif selection.startswith('test'):
            aa.test(N,T,C)
                        
        elif selection == 'exit':
            print('have a nice day')
            exit()
        else:
            print('command not recognized. type "help" for help')
            
if __name__ == '__main__':
    main()
