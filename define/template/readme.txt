2.1.	自动化生成C++数据结构

1	取得策划给出的模板表字段说明
1.1	字段说明在文件http://devnet/rainbow/DocLib4/数值文档/数值需求文档.docx中

2	构造数据表格式化定义xml文件
2.1	在src\defines\def_template目录下，新建模板数据表格式化定义xml文件
2.1.1	复制原有表定义xml文件，将其重命名
2.1.2	命名格式：结构名.xml
2.1.3	例：复制文件QuestData.xml，新建重命名文件NpcTemplate.xml
2.2	用文本编辑器打开新建好的表定义xml文件，修改其xml中数据结构元素名
2.2.1	修改后的xml元素名即为生成后的C++数据结构名
2.2.2	例：将xml元素名QuestData修改为NpcTemplate
2.3	用EXCEL打开新建好的表定义xml文件，填入所有字段名、字段类型、字段说明，并保存
2.3.1	字段类型只能用C++基本数据类型
2.3.2	可用字段类型
2.3.2.1	int
2.3.2.2	uint对应unsigned int
2.3.2.3	float
2.3.2.4	string 对应 char[]
2.3.2.5	bool 对应signed char
2.3.2.6	byte 对应signed char
2.3.3	string字符串类型需要填入字符串长度
2.4	用svn add添加已编辑好保存的表定义xml文件到svn库

3	用自动化脚本生成C++数据结构
3.1	在data\table_define目录下运行gen_localdata.bat文件，生成对应C++程序数据结构定义、EXCEL数据表定义、XDS加载资源文件
3.1.1	C++数据结构定义LocalDataType.h：根据src\defines\def_template目录下所有的模板表定义xml文件，在src\server\library\meta\generated目录下生成LocalDataType.h文件。该文件包含了根据所有模板表定义xml文件生成的C++数据结构定义
3.1.2	EXCEL数据表结构定义xml文件：在src\defines\def_template\excel目录下，生成可用EXCEL打开编辑的格式化xml文件，相当于已添加源的EXCEL文件。例：生成文件NpcTemplate_table.xml

4	将生成的表结构xml文件交由策划编辑
4.1	用svn add将src\defines\def_template\excel目录下生成的EXCEL数据表结构定义xml文件添加到svn库
4.2	将此文件交由策划进行数据编辑
