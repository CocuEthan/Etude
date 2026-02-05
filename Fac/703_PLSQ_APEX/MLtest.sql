BEGIN
  DBMS_DATA_MINING.CREATE_MODEL(
    model_name          => 'WORKOUT_CLUSTER_MODEL',
    mining_function     => dbms_data_mining.clustering,
    data_table_name     => 'FINAL_DATA_ML',
    case_id_column_name => 'ID',
    settings_table_name => 'WORKOUT_CLUSTER_SETTINGS'
  );
END;
/
