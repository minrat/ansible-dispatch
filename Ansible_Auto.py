#!/usr/bin/python

import re
import os
import commands

out=[]
def parse_session(IP, filename, tage):
    count=0
    try:
        start = False
        fobj = open(filename, 'r')
        lines = fobj.readlines()
        for eachLine in lines:
            if re.match('\[' + tage + '\]', eachLine):
                start = True
                count = count + 1
                continue
            if re.match('^\[', eachLine) and start:
                break
            if start :
                if '\n'!= eachLine:
                        count = count + 1
                        out.append(eachLine)
        fobj.close()
        #Get The Available Workers
        Workers=Get_Avaliable_Worker(IP)
        Workers=len(Workers)
        print "Workers is : "+str(Workers)
        #Caculate the flag
        flag=(count)/Workers

        order = Workers

        # Task Action Start
        Task_Action(tage, order, out)
    except IOError, e:
        print 'file open error: ', e
        return False

    return True
#Get Avaliable Worker
def Get_Avaliable_Worker(host):
        print "Get Avaliable Worker:"
        #(status, output) = commands.getstatusoutput("gearadmin -h "+host+" --workers | awk -F':' '{if($1>0){a=length($2);if(a!=0){print $0}}}'|awk -F \" \" {'print $5 \" \" $2'}")
        (status, output) = commands.getstatusoutput("gearadmin -h "+host+" --workers | awk -F':' '{if($1>0){a=length($2);if(a!=0){print $0}}}'|awk -F \" \" {'print $2'}")
        hosts=output.split('\n')
        return hosts

#Task (Directory And File)
def Task_Action(tage, Num, Content):
    temp_path="/etc/ansible/"
    for i in range(1,Num+1):
        if not os.path.exists(temp_path+str(i)):
                #Check the directory exist or not
                os.makedirs(temp_path+str(i))
                print "New File"+temp_path+str(i)+'/hosts'
                #Check the file exist or not
                if os.path.exists(temp_path+str(i)+'/hosts'):
                        pass
                else:
                        file_Num=file(temp_path+str(i)+'/hosts','w')
                        Write_Task_File(tage, temp_path+str(i), Num, i, Content)
                        file_Num.close()

#Write Into The Task File
def Write_Task_File(Tage, FilePath, Group, Order, Content):
        file_Order=file(FilePath+'/hosts','a')
        file_Order.write("["+Tage+"]\n")
        for i in range(0,len(Content)):
                File_Num = (i%Group) + 1
                if File_Num == Order:
                        file_Order.write(Content[i])
        file_Order.close()
        return True

#Dispatch The Task Into Workers
def Dispatch_Task(host,tag):
        temp_path="/etc/ansible/"
        hosts = Get_Avaliable_Worker(host)
        print "Count is : "+str(len(hosts))
        for i in range(0,len(hosts)):
                print hosts[i]
                print "scp -r "+temp_path+str(i+1)+"/hosts "+" "+"root"+"@"+hosts[i]+":"+temp_path
                (status, output) = commands.getstatusoutput("rsync "+temp_path+" "+"root"+"@"+hosts[i]+":"+temp_path)
                if status ==0:
                        print output
                        print "Remote Ansible Create Succeed!!"
                else :
                        print "Error!!"
                        print output
                (status, output) = commands.getstatusoutput("scp -r "+temp_path+str(i+1)+"/hosts "+"  "+"root"+"@"+hosts[i]+":"+temp_path)
                if status ==0:
                        print output
                        print "Succeed!!"
                else :
                        print "Error!!"
                        print output
                #Execute The Task
                output= Execute_Task(hosts[i], tag)
        return output

#Get The Current Server IP
def Get_Current_IP():
        print "Get Current IP:"
        (status, output) = commands.getstatusoutput("ifconfig -a|grep inet|grep -v 127.0.0.1|grep -v inet6|awk '{print $2}'|tr -d 'addr:'")
        return output

#
def Execute_Task(host, tag):
        print "Task Execute Phase Start"
        #Gearman Trigger Task
        cmd_execute="ansible "+tag+" -a 'hostname'"
        (status, output) = commands.getstatusoutput('ssh '+host+" "+cmd_execute)
        print output
        return output
        #Ansible Trigger Task
def main(IP):
    filename = "/etc/ansible/hosts"
    tage = "all"
    ip = IP
    while True:
        if len(filename) == 0:
           filename = raw_input('input the file name: ')
           if len(filename) == 0:
                print "ERROR: please give the file name"
        if len(tage) == 0:
           tage = raw_input('input the tage of the session: ')
           if len(tage) == 0:
                print "ERROR: please give the tage"
        if filename and tage:
           break

    result = parse_session(ip,filename, tage)
    if not result:
        print "ERROR: file parse the file"

    #Dispatch Task
    Dispatch_Task(IP,tage)

    #Execute The Ansible Task
    #result = Execute_Task(tage)
    return result

if __name__ == "__main__":
   IP=Get_Current_IP()
   main(IP)
