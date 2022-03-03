import rosbag2_py
import rclpy
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message, serialize_message

def get_rosbag_options(path, serialization_format='cdr'):
    storage_options = rosbag2_py.StorageOptions(uri=path, storage_id='sqlite3')

    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format=serialization_format,
        output_serialization_format=serialization_format)

    return storage_options, converter_options

def create_topic(writer, topic_name, topic_type, serialization_format='cdr'):
    topic_name = topic_name
    topic = rosbag2_py.TopicMetadata(name=topic_name, type=topic_type,
                                     serialization_format=serialization_format)
    writer.create_topic(topic)

def filter(bag_path_input,bag_path_output):

    storage_options, converter_options = get_rosbag_options(bag_path_input)
    storage_options2, converter_options2 = get_rosbag_options(bag_path_output)

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    writer = rosbag2_py.SequentialWriter()
    writer.open(storage_options2,converter_options2)

    topic_types = reader.get_all_topics_and_types()
    type_map = {topic_types[i].name: topic_types[i].type for i in range(len(topic_types))}

    for i in range(len(topic_types)):
        create_topic(writer, topic_types[i].name, topic_types[i].type)
    
    while reader.has_next():
        (topic, data, t) = reader.read_next()
        msg_type = get_message(type_map[topic])
        msg = deserialize_message(data, msg_type)

        if topic=="/tf":    
            if not ((msg.transforms[0].header.frame_id == "map" and msg.transforms[0].child_frame_id == "odom")):
                writer.write(topic,serialize_message(msg),t)
        else:
            writer.write(topic,serialize_message(msg),t)

filter("inputbag","outputbag")
