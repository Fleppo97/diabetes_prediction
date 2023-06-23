DROP KEYSPACE IF EXISTS diabetes_dataset;

CREATE KEYSPACE diabetes_dataset
  WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1};
  
  
USE diabetes_dataset;

CREATE TABLE features (
  id varchar PRIMARY KEY,
  Diabetes_binary DOUBLE,
  HighBP DOUBLE,
  HighChol DOUBLE,
  CholCheck DOUBLE,
  BMI DOUBLE,
  Smoker DOUBLE,
  Stroke DOUBLE,
  HeartDiseaseorAttack DOUBLE,
  PhysActivity DOUBLE,
  Fruits DOUBLE,
  Veggies DOUBLE,
  HvyAlcoholConsump DOUBLE,
  AnyHealthcare DOUBLE,
  NoDocbcCost DOUBLE,
  GenHlth DOUBLE,
  MentHlth DOUBLE,
  PhysHlth DOUBLE,
  DiffWalk DOUBLE,
  Sex DOUBLE,
  Age DOUBLE,
  Education DOUBLE,
  Income DOUBLE
);

SHOW HOST;

exit;
