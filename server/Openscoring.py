from openscoring import Openscoring


############################################
####### exporting pmml pipeline model ######
############################################
os = Openscoring("http://localhost:8080/openscoring")

#disonibile a http//localhost:8080/openscoring/model/Diabetes
os.deployFile("Diabetes", "/output/Diabetes.pmml")
