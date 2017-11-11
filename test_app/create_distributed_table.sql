SELECT create_distributed_table('stores_store','id');
SELECT create_distributed_table('stores_product','store_id');
SELECT create_distributed_table('stores_purchase','store_id');
