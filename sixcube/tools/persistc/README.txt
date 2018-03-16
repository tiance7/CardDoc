
1. daoSql2Xml.py工具
   用法：python daoSql2Xml.py mysql://root@10.1.0.51:3306/tk_188
   作用：会连接数据库，把库中所有表格的XML定义文件生成到output目录中
         可以用把需要的xml文件视情况确定是否需要修改，然后正式提交到defines目录中

2. daoXml2Cpp.py工具
   用法：python daoXml2Cpp.py <define file|dir> <outputdir>
   作用：会XML定义文件生成对应的CPP/H/SQL到output目录中         

3. daoXml2Go.py工具
   用法：python daoXml2Go.py <define file|dir> <outputdir>
   作用：会XML定义文件生成对应的go到output目录中         
