//
// Created by daniel on 22/11/24.
//

#ifndef VISION_ODOM_HPP
#define VISION_ODOM_HPP

#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <nav_msgs/msg/odometry.hpp>

#include <tf2_ros/transform_broadcaster.h>
#include <tf2_ros/transform_listener.h>
#include <tf2_ros/buffer.h>



class VisionOdom : public rclcpp::Node {
public:
    VisionOdom();
    void slam_pose_cb(const geometry_msgs::msg::PoseStamped::ConstSharedPtr msg);
    void ardu_pose_cb(const geometry_msgs::msg::PoseStamped::ConstSharedPtr msg);
    void timer_callback();
    void publish_tf(std::string parent, std::string child, const tf2::Transform &tf);
    void publish_ext_nav(const tf2::Transform &ext_nav);

private:

    // Subscribers
    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr slam_pose_sub_;
    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr ardu_pose_sub_;
    geometry_msgs::msg::PoseStamped slam_pose_;

    // Publsihers
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr ext_nav_pub_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;

    // Transform broadcaster
    std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
    std::shared_ptr<tf2_ros::Buffer> tf_buffer_;
    std::unique_ptr<tf2_ros::TransformListener> tf_listener_;

    // Timer
    rclcpp::TimerBase::SharedPtr timer_;

    // Parameters from node
    int timer_rate_;
    std::string map_frame_id_, slam_frame_id_, odom_frame_id_, base_frame_id_, camera_frame_id_;

    rclcpp::Duration slam_timeout_{std::chrono::milliseconds{0}};
    rclcpp::Duration transform_expiration_{std::chrono::milliseconds{1}};

    // Static transform
    tf2::Transform tf_cam_base_;
    // Dynamic transforms
    tf2::Transform tf_map_slam_;
    tf2::Transform tf_map_odom_;
    tf2::Transform tf_odom_base_;
    // Inverse transforms for speed & stability
    tf2::Transform tf_slam_map_;
    tf2::Transform tf_base_odom_;
};
#endif //VISION_ODOM_HPP
