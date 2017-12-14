from __future__ import print_function

import argparse
import os
import sys

import cifar10_dataset
import keras
from keras.callbacks import ModelCheckpoint
import resnet50_cifar10_model
import tensorflow as tf

# Training parameters
parser = argparse.ArgumentParser()

parser.add_argument(
    '--batch_size',
    type=int,
    default=32,
    help='Number of images to process in a batch')

parser.add_argument(
    '--epochs',
    type=int,
    default=2,
    help='Number of training steps')

def train(resnet50_cifar10_model, train_dataset, test_dataset, optimizer, loss_fn):
  train_dataset = train_dataset.batch(FLAGS.batch_size)
  test_dataset = test_dataset.batch(FLAGS.batch_size)

  (train_images, train_labels) = train_dataset.make_one_shot_iterator().get_next()
  train_images = tf.cast(train_images, tf.float32)
  train_labels = tf.cast(train_labels, tf.float32)
  (test_images, test_labels) = test_dataset.make_one_shot_iterator().get_next()
  test_images = tf.cast(test_images, tf.float32)
  test_labels = tf.cast(test_labels, tf.float32)

  model = resnet50_model(train_images)

  model.compile(loss=loss_fn,
                 optimizer=keras.optimizers.TFOptimizer(optimizer),
                target_tensors=[train_labels],
                metrics=['accuracy'])

  # Prepare model model saving directory.
  save_dir = os.path.join(os.getcwd(), 'saved_models')
  model_type = 'ResNet%dv%d' % (50, 1)
  model_name = 'cifar10_%s_model.{epoch:03d}.h5' % model_type
  if not os.path.isdir(save_dir):
    os.makedirs(save_dir)
  filepath = os.path.join(save_dir, model_name)
  # Prepare callbacks for model saving
  checkpoint = ModelCheckpoint(filepath=filepath,
                               monitor='val_acc',
                               verbose=1,
                               save_best_only=True)
  callbacks = [checkpoint]
  model.fit(steps_per_epoch=1, epochs=FLAGS.epochs, verbose=1,
            callbacks=callbacks)
  model.save_weights('saved_wt.h5')

  # Evaluate model
  test_model = resnet50_model(test_images)
  test_model.load_weights('saved_wt.h5')
  test_model.compile(optimizer=keras.optimizers.TFOptimizer(optimizer),
                     loss=loss_fn,
                     target_tensors=[test_labels],
                     metrics=['accuracy'])
  loss, acc = test_model.evaluate(steps=1, verbose=1)

  # Print eval results
  print('Test loss:', loss)
  print('Test accuracy:', acc)


def resnet50_model(train_images_tensors):
  depth = 50
  input_shape = (32, 32, 3)
  input_vals = keras.layers.Input(tensor=train_images_tensors)
  model = resnet50_cifar10_model.resnet_v1(input_shape=input_shape, depth=depth,
                                           input_tensor=input_vals)
  return model

def main(unparser):
  input_shape, train_dataset, test_dataset = cifar10_dataset.get_train_eval_dataset()

  train(resnet50_cifar10_model, train_dataset, test_dataset,
        tf.train.AdamOptimizer(learning_rate=0.001), loss_fn='categorical_crossentropy')

if __name__ == '__main__':
  tf.logging.set_verbosity(tf.logging.INFO)
  FLAGS, unparsed = parser.parse_known_args()
  tf.app.run(main=main, argv=[sys.argv[0]] + unparsed)


