*** Settings ***
Library    OperatingSystem
Library    Collections
Library    xenamanager.robot.xena_robot.XenaRobot

*** Variables ***
${CHASSIS}      176.22.65.114
@{PORTS}        ${CHASSIS}/6/4    ${CHASSIS}/6/5
${CONFIG_FILE}	${CURDIR}/test_config.xpc
${port0}        @{PORTS}[0]

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
    
Run Traffic
    [Documentation]    Run traffic and get statistics
    Clear Statistics
    Run Traffic Blocking
    &{stats} =         Get Statistics    Port
    Log Dictionary     ${stats}
    &{port_stats}      Set Variable    &{stats}[176.22.65.114/6/4]
    Log Dictionary     ${port_stats}
    &{pt_total_stats}  Set Variable    &{port_stats}[pt_total]
    Log Dictionary     ${pt_total_stats}
    Should Be Equal As Numbers    &{pt_total_stats}[packets]    16000    
