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

KongMing包含 API、Conductor、Agent三个组件，以及一个Nova Filter

- KongMing API: 接受来自用户或外部服务的请求，并返回响应结果
- KongMing Conductor: 接受来自API或Agent的内部RPC请求，访问数据库或对Agent进行操作
- KongMing Agent: Worker进程，部署于每个计算节点，接受RPC请求并进行相应的响应


架构图::

    +--------------+
    |              |
    | KongMing API +----------------+
    |              |              +-v--+
    +------+-------+              |    |
           |                      | DB |
           |                      |    |
     +-----v-------+              +-^--+
     |  KongMing   +----------------+
     |  Conductor  |
     +------+------+
            |
            |
            |
     +------v-----+
     |  KongMing  |
     |  Executor  |
     +------------+



How To Use
----------

Note ::
  VCPU pinning 不支持``QEMU``虚拟化。

1. 克隆代码::

  git clone https://github.com/zhengzhenyu/kongming.git

2. 安装::

  python setup.py install

3. 在kongming.conf中做如下配置::

  [oslo_messaging_notifications]

  transport_url = rabbit://{rabbit-pass}:root@{your-host}:5672/

  driver = messagingv2

