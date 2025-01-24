//
// Created by daniel on 22/11/24.
//

#include <vision_odom.hpp>


int main(int argc, char **argv) {
    // Initialize ROS2
    rclcpp::init(argc, argv);

    // Create and spin the node
    rclcpp::spin(std::make_shared<VisionOdom>());

    // Shutdown ROS2
    rclcpp::shutdown();
    return 0;
}

VisionOdom::VisionOdom() : Node("vision_odom") {
    this->declare_parameter<int>("timer_rate", 100);
    this->declare_parameter<std::string>("map_frame_id", "map");
    this->declare_parameter<std::string>("slam_frame_id", "orbslam3");
    this->declare_parameter<std::string>("odom_frame_id", "odom");
    this->declare_parameter<std::string>("base_frame_id", "base_link");
    this->declare_parameter<std::string>("camera_frame_id", "left_camera_link");

    this->get_parameter("timer_rate", timer_rate_);
    this->get_parameter("map_frame_id", map_frame_id_);
    this->get_parameter("slam_frame_id", slam_frame_id_);
    this->get_parameter("odom_frame_id", odom_frame_id_);
    this->get_parameter("base_frame_id", base_frame_id_);
    this->get_parameter("camera_frame_id", camera_frame_id_);

    rclcpp::QoS best_effort(10);
    best_effort.best_effort();

    rclcpp::QoS reliable(10);
    reliable.reliable();

    // Initialize the Transform Broadcaster
    tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this, best_effort);
    ext_nav_pub_ = create_publisher<geometry_msgs::msg::PoseStamped>("ext_nav", reliable);

    // Subscription to the pose topic
    slam_pose_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
        "camera_pose", // Adjust this to the topic name providing the PoseStamped
        best_effort,
        std::bind(&VisionOdom::slam_pose_cb, this, std::placeholders::_1));

    timer_ = this->create_wall_timer(std::chrono::milliseconds(1000 / timer_rate_),
                                     std::bind(&VisionOdom::timer_callback, this));

    // Get Static transform from base->cam and invert it to cam->base
    try {
        auto transform = tf_buffer_->lookupTransform(base_frame_id_, camera_frame_id_, tf2::TimePointZero);
        tf2::fromMsg(transform.transform, tf_cam_base_);
        tf_cam_base_ = tf_cam_base_.inverse();
    } catch (const tf2::TransformException &ex) {
        RCLCPP_ERROR(this->get_logger(), "Failed to lookup or invert transform: %s", ex.what());
    }
}

void VisionOdom::slam_pose_cb(const geometry_msgs::msg::PoseStamped::ConstSharedPtr msg) {
    auto tf_orb_cam = tf2::toMsg<geometry_msgs::msg::Pose, tf2::Transform>(msg->pose);
    auto tf_slam_base = tf_orb_cam * tf_cam_base_;
    tf_map_slam_ = tf_map_odom_ * tf_odom_base_ * tf_slam_map_;
    VisionOdom::publish_ext_nav(tf_map_slam_*tf_slam_base);
}

void VisionOdom::timer_callback() {
    VisionOdom::publish_tf(map_frame_id_, slam_frame_id_, tf_cam_base_);
    VisionOdom::publish_tf(map_frame_id_, odom_frame_id_, tf_map_odom_);
    VisionOdom::publish_tf(odom_frame_id_, base_frame_id_, tf_map_odom_);

    //TODO: use SLAM status to publish the ext navigation
    VisionOdom::publish_ext_nav(tf_map_odom_ * tf_odom_base_);
}

void VisionOdom::publish_tf(std::string parent, std::string child, const tf2::Transform &tf) {
    geometry_msgs::msg::TransformStamped tm;
    tm.header.frame_id = std::move(parent);
    tm.child_frame_id = std::move(child);
    tm.transform = tf2::toMsg<tf2::Transform, geometry_msgs::msg::Transform>(tf);
    // Adding time to the transform avoids problems and improves rviz2 display
    tm.header.stamp = now() + transform_expiration_;
    tf_broadcaster_->sendTransform(tm);
}

void VisionOdom::publish_ext_nav(const tf2::Transform &ext_nav) {
    geometry_msgs::msg::PoseStamped ext_nav_msg;
    ext_nav_msg.header.stamp = now();
    ext_nav_msg.header.frame_id = map_frame_id_;
    ext_nav_msg.pose = tf2::toMsg<tf2::Transform, geometry_msgs::msg::Pose>(ext_nav);
    ext_nav_pub_->publish(ext_nav_msg);
}
