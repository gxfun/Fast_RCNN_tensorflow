import sys
import numpy as np
# from vgg16 import vgg16
from base_bgg16 import Vgg
import tensorflow as tf
sys.path.append("/Users/tsujiyuuki/env_python/code/my_code/Data_Augmentation")

"""
・collect dataset of cars
・Preprocessing BBOX and Label for training
・try roi_pooling layer
・Extract ROI using mitmul tools
・NMS
"""

"""Flow of Fast RCNN
###############################################################################
In this state, Create Input Images and ROI Labels

1. input batch images and GroundTruth BBox from datasets *folder name, batch size
   Image shape is [batch size, width, height, channel], tf.float32, vgg normalized, bgr
   Bounding Box shape is [batch size, center_x, center_y, width, height]

2. get candicate bounding box from images.

   # Implemented
3. resize input images to input size   *size of resize    if needed.
   if this operation was done, you should adjust bounding box according to it.
   Both of Candicate and GroundTruth Bounding Boxes.
   In thesis, Image size is in [600, 1000]
   In this Implemention, input image has dynamic shape between [600, 1000]

4. convert candicate bounding box to ROI label.

5. calculate IOU between ROI label and GroundTruth label.
   IOU is Intersection Over Union.

6. Select Bounding Box from IOU.
   IOU > 0.5 is correct label, IOU = [0.1 0.5) is a false label(background).
   Correct Label is 25%, BackGround Label is 75%.
   Number of Label is 128, Batch Size is 2, so each image has 64 ROIs

###############################################################################
In this stage, Calculate Loss

7. Input data to ROI Pooling Layer is Conv5_3 Feature Map and ROIs
   Input shape is Feature map (batch, width, height, 512), ROIs (Num of ROIs, 5)
   ROIs, ex:) [0, left, height, right, bottom]. First Element is the index of batch

8. Through ROI Pooling Layer, Output Shape is [Num of ROIs, 7, 7, 512]

9. Reshape it to [Num of ROIs, -1], and then connect to Fully Connected Layer.

10.Output Layer has two section, one is class prediction, the other is its bounding box prediction.
   class prediction shape is [Num of ROIs, Num of Class + 1]
   bounding box prediction shape is [Num of ROIs, 4 * (Num of Class + 1)]

11.Loss Function
   Regularize bounding box value [center_x, center_y, w, h] into
   [(GroundTruth x / pred_x) / pred_w, (GroundTruth y / pred_y) / pred_h, GroundTruth w / pred_w, GroundTruth h / pred_h]
   Class prediction is by softmax with loss.
   Bounding Box prediction is by smooth_L1 loss
###############################################################################
In this stage, Describe Datasets.
1. PASCAL VOC2007
2. KITTI Datasets
3. Udacity Datasets
"""

def create_input_imgs(orig_img, shape=(500, 500)):
    """create input images for network from original images"""
    return resize_imgs, scales

def create_labels(resized_images, resize_scales, feature_scale=1./16):
    """create labels for classification and regression
    1. get bbox from resized images
    2. from bbox, create input labels for regression
    3. get GroundTruth Bounding Boxes
    4. calculate IOU for training
    5. divide labels into training sets and trush
    6.
    """
    return labels

def create_rois(labels, feature_scale=1./16):
    """create rois from labels"""
    return rois

def nms():
    return bboxes

def loss():
    pass

def data_augmentator(images, labels):
    """Data Augmentation *Not Resize transform
    1. Flip or Not
    2. vgg rescale
    """
    return images, labels

def im_list_to_blob(ims):
    """Convert a list of images into a network input.
    Assumes images are already prepared (means subtracted, BGR order, ...).
    """
    max_shape = np.array([im.shape for im in ims]).max(axis=0)
    num_images = len(ims)
    blob = np.zeros((num_images, max_shape[0], max_shape[1], 3),
                    dtype=np.float32)
    for i in xrange(num_images):
        im = ims[i]
        blob[i, 0:im.shape[0], 0:im.shape[1], :] = im
    return blob

def prep_im_for_blob(im, pixel_means, target_size=600, max_size=1000):
    """Mean subtract and scale an image for use in a blob."""
    im = im.astype(np.float32, copy=False)
    im -= pixel_means
    im_shape = im.shape
    im_size_min = np.min(im_shape[0:2])
    im_size_max = np.max(im_shape[0:2])
    im_scale = float(target_size) / float(im_size_min)
    # Prevent the biggest axis from being more than MAX_SIZE
    if np.round(im_scale * im_size_max) > max_size:
        im_scale = float(max_size) / float(im_size_max)
    im = cv2.resize(im, None, None, fx=im_scale, fy=im_scale,
                    interpolation=cv2.INTER_LINEAR)
    return im, im_scale

def data_generator(imgs, rois, labels):
    """data generator for network inputs"""
    yield batch_x, batch_rois, batch_labels

def get_bboxes(orig_img, im_scale, min_size, feature_scale=1. / 16):
    """Get Bounding Box from Original Image.

    # Args:
        orig_img   (ndarray): original image. 3 dimensional array.
        min_size     (tuple): minimum size of bounding box.
        feature_scale(float): scale of feature map. 2 ** (num of pooling layer)

    """
    rects = []
    dlib.find_candidate_object_locations(orig_img, rects, min_size=min_size)
    rects = [[0, d.left(), d.top(), d.right(), d.bottom()] for d in rects]
    rects = np.asarray(rects, dtype=np.float32)

    # bbox pre-processing
    rects *= im_scale
    v = np.array([1, 1e3, 1e6, 1e9, 1e12])
    hashes = np.round(rects * dedup_boxes).dot(v)
    _, index, inv_index = np.unique(hashes, return_index=True,
                                    return_inverse=True)
    rects = rects[index, :]

    return rects

def fast_rcnn(sess, rois, roi_size=(7, 7), vggpath=None, image_shape=(300, 300), \
              is_training=None, use_batchnorm=False, activation=tf.nn.relu, num_of_rois=128):
    """Model Definition of Fast RCNN
    In thesis, Roi Size is (7, 7), channel is 512
    """
    # images = tf.placeholder(tf.float32, [None, image_shape[0], image_shape[1], 3])
    # images = tf.placeholder(tf.float32, [None, image_shape[0], image_shape[1], 3])

    vgg = Vgg(vgg16_npy_path=vggpath)
    vgg.build_model(images)
    feature_map = vgg.conv5_3 # (batch, kernel, kernel, channel)

    with tf.variable_scope("fast_rcnn"):
        # roi shape [Num of ROIs, X, Y, W, H]
        roi_layer = roi_pooling(feature_map, rois, roi_size[0], roi_size[1])
        # input_shape [num_of_rois, channel, roi size, roi size]
        pool_5 = tf.reshape(roi_layer, [num_of_rois, roi_size[0]*roi_size[1]*512])
        fc6 = fully_connected(pool_5, [roi_size[0]*roi_size[1]*512, 4096], name="fc6", is_training=is_training)
        fc7 = fully_connected(fc6, [4096, 4096], name="fc7", is_training=is_training)
        # output shape [num_of_rois, 2]
        obj_class = tf.nn.softmax(fully_connected(fc7, [4096, 2], name="fc_class", activation=None, use_batchnorm=None), dim=-1)
        # output shape [num_of_rois, 8]
        bbox_regression = fully_connected(fc7, [4096, 8], name="fc_bbox", activation=None, use_batchnorm=None)

def fully_connected(input_layer, shape, name="", is_training=True, use_batchnorm=True, activation=tf.nn.relu):
    with tf.variable_scope("fully" + name):
        kernel = tf.get_variable("weights", shape=shape, \
            dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=0.01))
        fully = tf.matmul(input_layer, kernel)
        if activation:
            fully = activation(fully)
        if use_batchnorm:
            fully = batch_norm(fully, is_training)
        return fully

def batch_norm(inputs, is_training, decay=0.9, eps=1e-5):
    """Batch Normalization

       Args:
           inputs: input data(Batch size) from last layer
           is_training: when you test, please set is_training "None"
       Returns:
           output for next layer
    """
    gamma = tf.Variable(tf.ones(inputs.get_shape()[1:]), name="gamma")
    beta = tf.Variable(tf.zeros(inputs.get_shape()[1:]), name="beta")
    pop_mean = tf.Variable(tf.zeros(inputs.get_shape()[1:]), trainable=False, name="pop_mean")
    pop_var = tf.Variable(tf.ones(inputs.get_shape()[1:]), trainable=False, name="pop_var")

    if is_training != None:
        batch_mean, batch_var = tf.nn.moments(inputs, [0])
        train_mean = tf.assign(pop_mean, pop_mean * decay + batch_mean*(1 - decay))
        train_var = tf.assign(pop_var, pop_var * decay + batch_var * (1 - decay))
        with tf.control_dependencies([train_mean, train_var]):
            return tf.nn.batch_normalization(inputs, batch_mean, batch_var, beta, gamma, eps)
    else:
        return tf.nn.batch_normalization(inputs, pop_mean, pop_var, beta, gamma, eps)

def convBNLayer(input_layer, use_batchnorm, is_training, input_dim, output_dim, \
                kernel_size, stride, activation=tf.nn.relu, padding="SAME", name="", atrous=False, rate=1):
    with tf.variable_scope("convBN" + name):
        w = tf.get_variable("weights", \
            shape=[kernel_size, kernel_size, input_dim, output_dim], initializer=tf.contrib.layers.xavier_initializer())

        if atrous:
            conv = tf.nn.atrous_conv2d(input_layer, w, rate, padding="SAME")
        else:
            conv = tf.nn.conv2d(input_layer, w, strides=[1, stride, stride, 1], padding=padding)

        if use_batchnorm:
            bn = batch_norm(conv, is_training)
            if activation != None:
                return activation(conv, name="activation")
            return bn

        b = tf.get_variable("bias", \
            shape=[output_dim], initializer=tf.constant_initializer(0.0))
        bias = tf.nn.bias_add(conv, b)
        if activation != None:
            return activation(bias, name="activation")
        return bias

def maxpool2d(x, kernel=2, stride=1, name="", padding="SAME"):
    """define max pooling layer"""
    with tf.variable_scope("pool" + name):
        return tf.nn.max_pool(
            x,
            ksize = [1, kernel, kernel, 1],
            strides = [1, stride, stride, 1],
            padding=padding)

class ExtendedLayer(object):
    def __init__(self):
        pass

    def build_model(self, input_layer, use_batchnorm=False, is_training=True, atrous=False, \
                    rate=1, activation=tf.nn.relu, implement_atrous=False, lr_mult=1):
        if implement_atrous:
            if atrous:
                self.pool_5 = maxpool2d(input_layer, kernel=3, stride=1, name="pool5", padding="SAME")
            else:
                self.pool_5 = maxpool2d(input_layer, kernel=2, stride=2, name="pool5", padding="SAME") #TODO: padding is valid or same

            kernel_size = 3
            if atrous:
                rate *= 6
                # pad = int(((kernel_size + (rate - 1) * (kernel_size - 1)) - 1) / 2)
                self.conv_6 = convBNLayer(self.pool_5, use_batchnorm, is_training, 512, 1024, kernel_size, 1, \
                                          name="conv_6", activation=tf.nn.relu, atrous=True, rate=rate)
            else:
                rate *= 3
                # pad = int(((kernel_size + (rate - 1) * (kernel_size - 1)) - 1) / 2)
                self.conv_6 = convBNLayer(self.pool_5, use_batchnorm, is_training, 512, 1024, kernel_size, 1, \
                                          name="conv_6", activation=tf.nn.relu, atrous=True, rate=rate)
        else:
            self.pool_5 = maxpool2d(input_layer, kernel=3, stride=1, name="pool5", padding="SAME")
            self.conv_6 = convBNLayer(self.pool_5, use_batchnorm, is_training, 512, 1024, 3, 1, \
                                      name="conv_6", activation=tf.nn.relu, atrous=False, rate=rate)

        self.conv_7 = convBNLayer(self.conv_6, use_batchnorm, is_training, 1024, 1024, 1, 1, name="conv_7", activation=activation)
        self.conv_8_1 = convBNLayer(self.conv_7, use_batchnorm, is_training, 1024, 256, 1, 1, name="conv_8_1", activation=activation)
        self.conv_8_2 = convBNLayer(self.conv_8_1, use_batchnorm, is_training, 256, 512, 3, 2, name="conv_8_2", activation=activation)
        self.conv_9_1 = convBNLayer(self.conv_8_2, use_batchnorm, is_training, 512, 128, 1, 1, name="conv_9_1", activation=activation)
        self.conv_9_2 = convBNLayer(self.conv_9_1, use_batchnorm, is_training, 128, 256, 3, 2, name="conv_9_2", activation=activation)
        self.conv_10_1 = convBNLayer(self.conv_9_2, use_batchnorm, is_training, 256, 128, 1, 1, name="conv_10_1", activation=activation)
        self.conv_10_2 = convBNLayer(self.conv_10_1, use_batchnorm, is_training, 128, 256, 3, 1, name="conv_10_2", activation=activation, padding="VALID")
        self.conv_11_1 = convBNLayer(self.conv_10_2, use_batchnorm, is_training, 256, 128, 1, 1, name="conv_11_1", activation=activation)
        self.conv_11_2 = convBNLayer(self.conv_11_1, use_batchnorm, is_training, 128, 256, 3, 1, name="conv_11_2", activation=activation, padding="VALID")

def ssd_model(sess, vggpath=None, image_shape=(300, 300), \
              is_training=None, use_batchnorm=False, activation=tf.nn.relu, \
              num_classes=0, normalization=[], atrous=False, rate=1, implement_atrous=False):
    """
       1. input RGB images and labels
       2. edit images like [-1, image_shape[0], image_shape[1], 3]
       3. Create Annotate Layer?
       4. input x into Vgg16 architecture(pretrained)
       5.
    """
    images = tf.placeholder(tf.float32, [None, image_shape[0], image_shape[1], 3])
    vgg = Vgg(vgg16_npy_path=vggpath)
    vgg.build_model(images)

    with tf.variable_scope("extended_model") as scope:
        phase_train = tf.placeholder(tf.bool, name="phase_traing") if is_training else None
        extended_model = ExtendedLayer()
        extended_model.build_model(vgg.conv5_3, use_batchnorm=use_batchnorm, atrous=atrous, rate=rate, \
                                   is_training=phase_train, activation=activation, lr_mult=1, implement_atrous=implement_atrous)

    # with tf.variable_scope("multibox_layer"):
    #     from_layers = [vgg.conv4_3, extended_model.conv_7, extended_model.conv_8_2,
    #                    extended_model.conv_9_2, extended_model.conv_10_2, extended_model.conv_11_2]
    #     multibox_layer = MultiboxLayer()
    #     multibox_layer.build_model(from_layers, num_classes=0, normalization=normalization)
    #
    initialized_var = tf.get_collection(tf.GraphKeys.GLOBAL_VARIABLES, scope="extended_model")
    sess.run(tf.variables_initializer(initialized_var))

    return extended_model

class MultiboxLayer(object):
    def __init__(self):
        pass

    # TODO: validate this is correct or not
    def l2_normalization(self, input_layer, scale=20):
        return tf.nn.l2_normalize(input_layer, dim) * scale

    def createMultiBoxHead(self, from_layers, num_classes=0, normalizations=[], \
                           use_batchnorm=False, is_training=None, activation=None, \
                           kernel_size=3, prior_boxes=[], kernel_sizes=[]):
        """
           # Args:
               from_layers(list)   : list of input layers
               num_classes(int)    : num of label's classes that this architecture detects
               normalizations(list): list of scale for normalizations
                                     if value <= 0, not apply normalization to the specified layer
        """
        assert num_classes > 0, "num of label's class  must be positive number"
        if normalizations:
            assert len(from_layers) == len(normalizations), "from_layers and normalizations should have same length"

        num_list = len(from_layers)
        for index, kernel_size, layer, norm in zip(range(num_list), kernel_sizes, from_layers, normalizations):
            input_layer = layer
            with tf.variable_scope("layer" + str(index+1)):
                if norm > 0:
                    scale = tf.get_variable("scale", trainable=True, initializer=tf.constant(norm))#initialize = norm
                    input_layer = self.l2_normalization(input_layer, scale)

                # create location prediction layer
                loc_output_dim = 4 * prior_num # (center_x, center_y, width, height)
                location_layer = convBNLayer(input_layer, use_batchnorm, is_training, input_layer.get_shape()[0], loc_output_dim, kernel_size, 1, name="loc_layer", activation=activation)
                # from shape : (batch, from_kernel, from_kernel, loc_output_dim)
                # to         : (batch, )
                location_pred = tf.reshape(location_layer, [-1, ])

                # create confidence prediction layer
                conf_output_dim = num_classes * prior_num
                confidence_layer = convBNLayer(input_layer, use_batchnorm, is_training, input_layer.get_shape()[0], conf_output_dim, kernel_size, 1, name="conf_layer", activation=activation)
                confidence_pred = tf.reshape(confidence_pred, [-1, ])

                # Flatten each output

                # append result of each results

        return None

if __name__ == '__main__':
    import sys
    import matplotlib.pyplot as plt
    from PIL import Image as im
    sys.path.append('/home/katou01/code/grid/DataAugmentation')
    from resize import resize

    image = im.open("./test_images/test1.jpg")
    image = np.array(image, dtype=np.float32)
    new_image = image[np.newaxis, :]
    batch_image = np.vstack((new_image, new_image))
    batch_image = resize(batch_image, size=(300, 300))

    with tf.Session() as sess:
        model = ssd_model(sess, batch_image, activation=None, atrous=False, rate=1, implement_atrous=False)
        print(vars(model))
        # tf.summary.scalar('model', model)
