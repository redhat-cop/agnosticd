FROM docker-registry.default.svc:5000/openshift/rhpam-kieserver-rhel8:7.5.0

# jPMML
ADD https://search.maven.org/remotecontent?filepath=org/jpmml/pmml-evaluator/1.4.9/pmml-evaluator-1.4.9.jar /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/pmml-evaluator-1.4.9.jar
ADD https://search.maven.org/remotecontent?filepath=org/jpmml/pmml-evaluator-extension/1.4.9/pmml-evaluator-extension-1.4.9.jar /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/pmml-evaluator-extension-1.4.9.jar
ADD https://search.maven.org/remotecontent?filepath=org/kie/kie-dmn-jpmml/7.27.0.Final/kie-dmn-jpmml-7.27.0.Final.jar /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/kie-dmn-jpmml-7.27.0.Final.jar

COPY contrib/gdemo-prometheus-metrics-provider-1.0.0.jar /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/gdemo-prometheus-metrics-provider-1.0.0.jar

USER root
RUN chown jboss:root /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/pmml-evaluator-1.4.9.jar && \
			chown jboss:root /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/pmml-evaluator-extension-1.4.9.jar && \
      chown jboss:root /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/kie-dmn-jpmml-7.27.0.Final.jar && \
			chown jboss:root /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/gdemo-prometheus-metrics-provider-1.0.0.jar && \
			chmod 664 /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/pmml-evaluator-1.4.9.jar && \
			chmod 664 /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/pmml-evaluator-extension-1.4.9.jar && \
      chmod 664 /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/kie-dmn-jpmml-7.27.0.Final.jar && \
			chmod 664 /opt/eap/standalone/deployments/ROOT.war/WEB-INF/lib/gdemo-prometheus-metrics-provider-1.0.0.jar

USER jboss
