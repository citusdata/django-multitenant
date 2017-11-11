ALTER TABLE public.stores_purchase DROP CONSTRAINT stores_purchase_pkey;
ALTER TABLE stores_product DROP CONSTRAINT stores_product_pkey;
ALTER TABLE stores_product DROP CONSTRAINT stores_product_store_id_6ebcf184_fk_stores_store_id;
ALTER TABLE public.stores_purchase DROP constraint stores_purchase_store_id_00c5b29b_fk_stores_store_id;
select create_distributed_table('stores_product','store_id');
select create_distributed_table('stores_store','id');
select create_distributed_table('stores_store','id');
