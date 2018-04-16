*** Settings ***
Library    OperatingSystem
Library    Collections
Library    xena_robot.XenaRobot

*** Variables ***
${CHASSIS}      176.22.65.114
@{PORTS}        ${CHASSIS}/6/4    ${CHASSIS}/6/5
${CONFIG_FILE}	${CURDIR}/test_config.xpc

*** Keywords ***
Reserve All Ports
    [Documentation]    Reserve ports and load same configuration on all ports.
    Log List           ${PORTS}     
    Reserve Ports      @{PORTS}
    :FOR    ${PORT}    IN    @{PORTS}
    \    Load Config        ${PORT}    ${CONFIG_FILE}

*** Test Cases ***
Connect
    [Documentation]    Open session and connect to Xena Chassis
    Add Chassis        ${CHASSIS}
    Reserve All Ports

Investigate Configuration
    [Documentation]        Investigate laded configuration for port 0
    ${p_txmode} =          Get Port Attribute    @{PORTS}[0]    p_txmode 
    Log                    p_config = ${p_txmode}
    ${ps_packetlimit} =    Get Stream Attribute     @{PORTS}[0]    0    ps_packetlimit
    Log                    ps_packetlimit = ${ps_packetlimit}
    ${headers} =           Get Packet Headers    @{PORTS}[0]    1
    Log                    headers = ${headers}
    &{header} =            Get Packet Header    @{PORTS}[0]    1    Ethernet
    Log Dictionary         ${header}
    &{header} =            Get Packet Header    @{PORTS}[0]    1    VLAN[0]
    Log Dictionary         ${header}
    &{header} =            Get Packet Header    @{PORTS}[0]    1    IP6
    Log Dictionary         ${header}

Build Configuration
    Pass Execution         Dont care at this point...
    [Documentation]        Build new configuration for port 1
    Reset Port             @{PORTS}[1]
    Set Port Attributes    @{PORTS}[1]    p_txmode=NORMAL
    Add Stream             @{PORTS}[1]    stream 0
    # Call stream commands with stream ID
    Set Stream Attributes  @{PORTS}[1]    0    ps_packetlimit=80    ps_ratepps=10
    Add Stream             @{PORTS}[1]    stream 1
    # Call stream commands with stream name
    Set Stream Attributes  @{PORTS}[1]    stream 1    ps_packetlimit=80    ps_ratepps=10

Miscelenious Operations
    Pass Execution         Dont care at this point...
    [Documentation]        Run miscelenious commands
    ${c_comment} =         Exec Command    c_comment ?
    Log                    c_comment = ${c_comment}
    ${p_comment} =         Exec Command    6/4 p_comment ?
    Log                    p_comment = ${p_comment}
    ${rc} =                Exec Command    6/4 p_comment "new comment"
    Log                    rc = ${rc}

Run Traffic
    Pass Execution     Dont care at this point...
    [Documentation]    Run traffic and get statistics
    Clear Statistics   0 1
    Run Traffic Blocking
    &{stats} =         Get Statistics    Port
    ${keys} =          Get Dictionary Keys    ${stats}
    &{port_stats}      Set Variable    &{stats}[176.22.65.114/6/4]
    Log Dictionary     ${port_stats}
    &{pt_total_stats}  Set Variable    &{port_stats}[pt_total]
    Log Dictionary     ${pt_total_stats}
    Should Be Equal As Numbers    &{pt_total_stats}[packets]    16000  
