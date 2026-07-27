4.8 QoS based resource optimization 
4.8.1 Background information 
QoS based resource optimization can be used when the network has been configured to provide some kind of preferential 
QoS for certain users. One such scenario can be related to when the network has been configured to support e2e slices. In 
this case, the network has functionality that ensures resource isolation between slices as well as functionality to monitor 
that slice Service Level Specifications (SLS) are fulfilled.  
In RAN, it is the scheduler that ensures that Physical Resource Block (PRB) resources are isolated between slices in the 
best possible way and also that the PRB resources are used in an optimal way to best fulfill the SLS for different slices. 
The desired default RAN behavior for slices is configured over O1. For example, the ratio of physical resources (PRBs) 
reserved for a slice is configured at slice creation (instantiation) over O1. Also, QoS can be configured to guide the RAN 
scheduler how to (in real-time) allocate PRB resources to different users to best fulfill the SLS of a specific slice. In the 
NR NRM this is described by the resource partition attribute. 
Instantiation of a RAN sub-slice will be prepared by rigorous planning to understand to what extent deployed RAN 
resources will be able to support RAN sub-slice SLS. Part of this procedure is to configure RAN functionality according 
to above. With this, a default behavior of RAN is obtained that will be able to fulfill slice SLSs for most situations. 
However, even through rigorous planning, there will be times and places where the RAN resources are not enough to 
fulfill SLS given the default configuration. To understand how often (and where) this happens, the performance of a RAN 
slice will continuously be monitored by SMO. When SMO detects a situation when RAN SLS cannot be fulfilled, Non
RT RIC can use A1 policies to improve the situation. To understand how to utilize A1 policies and how to resolve the 
situation, the Non-RT RIC will use additional information available in SMO. 

4.8.2 Motivation 
To motivate the use case an example with an emergency service as a slice tenant is used. For this example, it is understood 
(at slice instantiation) that 50% of the PRBs in an area can be enough to support the emergency traffic under normal 
circumstances. Therefore, the ratio of PRBs for the emergency users is configured to 50% as default behavior for the pre
defined group of users belonging to the emergency slice. Also, QoS is also configured in CN and RAN so that video 
cameras of emergency users get a minimum bitrate of 500 kbps. 
Now, suppose a large fire is ongoing and emergency users are on duty. Some of the personnel capture the fire on video 
on site. The video streams are available to the emergency control command. Because of the high traffic demand in the 
area from several emergency users (belonging to the same slice), the resources available for the emergency slice is not 
enough to support all the traffic. In this situation, the operator has several possibilities to mitigate the situation. Depending 
on SLAs towards the emergency slice compared to SLAs for other slices, the operator could reconfigure the amount of 
PRB reserved to emergency slice at the expense of other slices. However, there is always a risk that emergency video 
quality is not good enough irrespective if all resources are used for emergency users. It might be that no video shows 
sufficient resolution due to resource limitations around the emergency site. 
In this situation, the emergency control command decides, based on the video content, to focus on a selected video stream 
to improve the resolution. The emergency control system gives the information about which users to up- and down
prioritized to the e2e slice assurance function (through e.g., an Edge API) of the mobile network to increase bandwidth 
for selected video stream(s). Given this additional information, the Non-RT RIC can influence how RAN resources are 
allocated to different users through a QoS target statement in an A1 policy. By good usage of the A1 policy, the emergency 
control command can ensure that dynamically defined group of UEs provides the video resolution that is needed.  
The use case can be summarized as per below: 
• A fire draws a lot of emergency personnel to an area. 
• Because of this RAN resources becomes congested which affects the video quality for all video feeds in the area. 
• The emergency control command have 5 active video feeds and selects one video feed which is of specific 
interest. 
• The emergency control command requests higher resolution of a selected feed, while demoting the other. 
• With this information, the Non-RT RIC will evaluate how to ensure higher bandwidth for the feed selected by 
emergency control command (and lower for other feeds). 
• The Non-RT RIC updates the policy for the associated UEs in the associated Near-RT RIC over the A1 interface. 
• Near-RT RIC enforce the modified QoS target for the associated UEs over the E2 interface to fulfill the request. 
• The emergency control command experiences a higher resolution of the selected video feed. 

4.8.3 Proposed solution 
The main functions of the O-RAN components are utilized to support an improved QoS based resource optimization. QoS 
based resource optimization use case deploys O-CU, O-DU, the Non-RT RIC and the Near-RT RIC function modules. To 
achieve intelligent resource optimization, Non-RT RIC should provide policies to Near-RT RIC which are used to drive 
QoS based resource optimization at the RAN level. Non-RT RIC should monitor QoS related metrics from network and 
SMO functions. O-CU and O-DU components should provide UE performance metrics with the configured granularity 
to SMO via O1.  In addition to performance metrics retrieved from network elements, external information sources might 
also be utilized to solve the problem of allocation limited RAN resources. For example, external server could provide 
Non-RAN data about priorities of the UEs to SMO.  Finally, the E2 nodes should execute QoS enforcement decisions 
received from Near-RT RIC which are expected to influence RRM behaviour.   

4.8.4 Benefits of O-RAN architecture 
The main features of O-RAN architecture are pointed by the proposed solution which aims to offer more advanced QoS 
based resource optimization.