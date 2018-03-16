all: struct entity meta

entity: test.py persist_entity.stg charitem.proto
	test.py persist_entity.stg charitem.proto

struct: test.py proto_cpp.stg charitem.proto
	test.py proto_cpp.stg charitem.proto

meta: metac.py proto_meta.stg char.proto
      metac.py char.proto

item: test.py proto_meta.stg charitem.proto
      test.py proto_meta.stg charitem.proto




