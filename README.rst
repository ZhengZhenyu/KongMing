KongMing (孔明）
==============

配合OpenStack Nova的虚拟机VCPU、NUMA、RAM部署优化工具。

Usecase
-------

1. NFV

在NFV场景中，性能往往非常重要。NFV客户通常会有将虚拟机的CPU、RAM放置在同一NUMA上的需求来
提升整体性能。对于更专业的用户，他们通常有自己的编排工具(MANO)及高级的性能调优算法，通过这
套工具他们会计算出能够满足他们性能需求且最优化资源占用的部署模板，他们会期望使用这套模板来部
署集群并且希望在必要的时候能够动态的调整模板。

对于OpenStack这种通用云平台来说，这种对资源的高度控制力显然是不够”云化“的，但是这种使用方
式对于NFV用户来说又是相当重要的。

2. 公有云、私有云

在公有云、私有云场景中，管理员可能需要在不同的时段对有着不同性能要求的虚拟机有动态调整的需求。
通过这套方案还能实现vcpu级别的Qos。

Idea
----

此项目应运而生，目标是在OpenStack Nova外围实现一套工具，在不影响原生Nova API的前提下，
为NFV用户实现对于虚拟机VCPU、RAM部署的精确控制，以及动态调整。

Implementation
--------------

本项目的主要思路是在虚拟机创建成功后，通过某种机制触发部署在每一个计算节点上的``Executor``
通过获取到的部署模板调用``Hypervisor``来进行相应的操作。触发机制分为以下三类

1. Versioned Notification + Instance Metadata (已经实现）

* 优点:

  - 实现简单
  - 没有额外的API调用

* 缺点:

  - 依赖于``Versioned Nofitication`` 及 ``Instance Metadata``
  - 不利于功能扩展
    
  架构图::

               +-----------------+
               |  Message Queue  |
               +-------------+---+
                   ^         |
            Listen |         | Versioned Notification
                   |         |
                   |         v
          +--------+----------------------+
          | KongMing Notification Handler |
          +-------------+-----------------+
                        |
                        |   Notification.Type == instance.create.end
                        |   Notification.Payload.Host == self.host
                        |
              +---------v----------+
              |  KongMing Executor |
              +---------+----------+
                        |
                        | Payload Parse
                 +------v--------+
                 |    Libvirt    |
                 +---------------+


2. Legacy Notification + Instance Metadata + Novaclient(未实现）
  
* 优点:

  - 实现中等

* 缺点:

  - 需要从计算节点通过API调用Nova-API
  - 依赖于``Instance Metadata``(用户可见）
  - 不利于功能扩展

  架构图::
    
              +-----------------+
              |  Message Queue  |
              +---+---------+---+
                  |         |
           Listen |         |  Legacy Notification
                  |         |
                  |         |
         +--------+---------v------------+
         | KongMing Notification Handler |
         +-------------+-----------------+
                       |
                       |   Notification.Type == instance.create.end
                       |   Notification.Publisher_id:host == self.host
                       |
             +---------v----------+  GET /server/{uuid}details    +---------------+
             |  KongMing Executor +  ------------------------>    |   Nova-API    |
             +---------+----------+  <-----------------------+    +---------------+
                       |                 instance.metadata
                       | Metadata Parse
                +------v--------+
                |    Libvirt    |
                +---------------+
         

3. Stand-alone (API + DB +Executor)(未实现）

* 优点:

  - 功能扩展性强

* 缺点:

  - 实现复杂

架构图::

                                               Polling   +------------+
                                              +--------> |  Nova API  |
                                              |          +------------+
          Allocation Map      +-------------++
        +------------------>  | KongMing API |       +---------------+
                              +------+------++       | Message Queue |
                                     |      |        +---------------+
                       Allocation Map|      +-------------^
                                     |       Listen
                           +---------v---------+
                           | KongMing Executor |
                           +---------+---------+
                                     |
                                     |
                               +-----V-----+
                               |  Libvirt  |
                               +-----------+


How To Use
----------

Note ::
  VCPU pinning 不支持``QEMU``虚拟化。

目前仅实现了第一种触发模式(Versioned Notification + Instance Metadata)

1. 克隆代码::

  git clone https://github.com/zhengzhenyu/kongming.git

2. 安装::

  python setup.py install

3. 在kongming.conf中做如下配置::

  [oslo_messaging_notifications]

  transport_url = rabbit://{rabbit-pass}:root@{your-host}:5672/

  driver = messagingv2

4. 启动服务::

  python /usr/local/bin/kongming-notification-handler --config-file=kongming.conf

5. 在创建虚拟机时使用``metadata key``触发功能::

  nova boot ... --meta kongming-vcpu-pinning=5-6,9-11,^10  test
