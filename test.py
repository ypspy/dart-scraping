# -*- coding: utf-8 -*-
"""
Created on Sat Jun  4 23:40:43 2022

@author: yoonseok
"""

import js2py

code = """
var cnt = 0;
var treeData = [];

var node1 = {};
node1["text"] = "감   사   보   고   서";
node1["id"] = "1";
node1["rcpNo"] = "20220321001420";
node1["dcmNo"] = "8487091";
node1["eleId"] = "1";
node1["offset"] = "1710";
node1["length"] = "1337";
node1["dtd"] = "dart3.xsd";
node1["tocNo"] = "1"; //eleId 가 toc 순번하고 동일 하지 않은 문서가 존재함.

cnt++;

treeData.push(node1);

var node1 = {};
node1["text"] = "독립된 감사인의 감사보고서";
node1["id"] = "2";
node1["rcpNo"] = "20220321001420";
node1["dcmNo"] = "8487091";
node1["eleId"] = "2";
node1["offset"] = "4191";
node1["length"] = "6029";
node1["dtd"] = "dart3.xsd";
node1["tocNo"] = "2"; //eleId 가 toc 순번하고 동일 하지 않은 문서가 존재함.

cnt++;

treeData.push(node1);

var node1 = {};
node1["text"] = "(첨부)재 무 제 표";
node1["id"] = "3";
node1["rcpNo"] = "20220321001420";
node1["dcmNo"] = "8487091";
node1["eleId"] = "3";
node1["offset"] = "10250";
node1["length"] = "350355";
node1["dtd"] = "dart3.xsd";
node1["tocNo"] = "3"; //eleId 가 toc 순번하고 동일 하지 않은 문서가 존재함.

cnt++;

node1["children"] = [];

var node2 = {};
node2["text"] = "주석";
node2["id"] = "4";
node2["rcpNo"] = "20220321001420";
node2["dcmNo"] = "8487091";
node2["eleId"] = "4";
node2["offset"] = "78061";
node2["length"] = "282530";
node2["dtd"] = "dart3.xsd";
node2["tocNo"] = "4"; //eleId 가 toc 순번하고 동일 하지 않은 문서가 존재함.

cnt++;

node1["children"].push(node2);

treeData.push(node1);

var node1 = {};
node1["text"] = "내부회계관리제도 감사 또는 검토의견";
node1["id"] = "5";
node1["rcpNo"] = "20220321001420";
node1["dcmNo"] = "8487091";
node1["eleId"] = "5";
node1["offset"] = "361021";
node1["length"] = "2843";
node1["dtd"] = "dart3.xsd";
node1["tocNo"] = "5"; //eleId 가 toc 순번하고 동일 하지 않은 문서가 존재함.

cnt++;

treeData.push(node1);

var node1 = {};
node1["text"] = "외부감사 실시내용";
node1["id"] = "6";
node1["rcpNo"] = "20220321001420";
node1["dcmNo"] = "8487091";
node1["eleId"] = "6";
node1["offset"] = "363894";
node1["length"] = "22549";
node1["dtd"] = "dart3.xsd";
node1["tocNo"] = "6"; //eleId 가 toc 순번하고 동일 하지 않은 문서가 존재함.

cnt++;
"""

test = js2py.eval_js('console.log("Hello World"')

