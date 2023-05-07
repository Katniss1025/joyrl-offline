#!/usr/bin/env python
# coding=utf-8
'''
Author: JiangJi
Email: johnjim0816@gmail.com
Date: 2023-05-07 18:30:53
LastEditor: JiangJi
LastEditTime: 2023-05-08 00:23:46
Discription: 
'''
import ray
@ray.remote
class Learner:
    def __init__(self,cfg,policy=None,data_handler=None) -> None:
        self.cfg = cfg
        self.policy = policy
        self.data_handler = data_handler
    def add_transition(self,transition):
        self.data_handler.add_transition(transition)
    def get_action(self,state,data_server = None):
        data_server.increase_sample_count.remote()
        sample_count = ray.get(data_server.get_sample_count.remote())
        return self.policy.get_action(state,sample_count=sample_count)
    def train(self,data_server = None, stats_recorder = None):
        # print("Learner is training")
        data_server.increase_update_step.remote()
        self.update_step = ray.get(data_server.get_update_step.remote())
        training_data = self.data_handler.sample_training_data()
        if training_data is not None:
            self.policy.update(**training_data,update_step=self.update_step)
            self.add_policy_summary(stats_recorder)
            
    def add_policy_summary(self, stats_recorder):
        summary = self.policy.summary
        stats_recorder.add_policy_summary.remote((self.update_step,summary))

