package template

import (
	"bytes"
	"encoding/xml"
	"io/ioutil"
)

const (
	_${T_NAME}s_root string = "g_${T_NAME}"
)

var (
	_${T_NAME}_templates ${T_NAME}s
	_${T_NAME}_table     map[${xmldef.get_key_type()}]${T_NAME}Map
    _${T_NAME}_load      bool
)

func init() {
	_${T_NAME}_table = make(map[${xmldef.get_key_type()}]${T_NAME}Map)
    _${T_NAME}_load = false
}

type ${T_NAME}Map map[uint32]*${T_NAME}

type ${T_NAME}s struct {
	XMLName xml.Name             `xml:"g_${T_NAME}"`
	Entries []${T_NAME} `xml:"entry"`
}

type ${T_NAME} struct {
    DataExcept      uint32      `xml:"nDataExcept"`         // version except flags
    DataDiff        uint32      `xml:"nDataDiff"`           // version differentiation flags
% for field in fields:
    ${xmldef.get_fname(field,True)}        ${xmldef.get_ftype(field)}      `xml:"${xmldef.get_fname(field)}"`       // ${xmldef.get_fcomment(field)}
% endfor
}

func ReLoad${T_NAME}(xmlfile string, dataVer uint32) error {
    _${T_NAME}_table = make(map[${xmldef.get_key_type()}]${T_NAME}Map)
    _${T_NAME}_load = false
    return Load${T_NAME}(xmlfile, dataVer)
}

// Load ${T_NAME}(s) from xml template.
func Load${T_NAME}(xmlfile string, dataVer uint32) error {
    if _${T_NAME}_load {
        return nil
    }
    
	content, err := ioutil.ReadFile(xmlfile)
	if err != nil {
		return err
	}

	root := bytes.Index(content, []byte("<"+_${T_NAME}s_root+">"))
	rootEnd := bytes.Index(content, []byte("</"+_${T_NAME}s_root+">"))

	err = xml.Unmarshal(content[root:rootEnd+3+len(_${T_NAME}s_root)], &_${T_NAME}_templates)
	if err != nil {
		return err
	}

	for i, _ := range _${T_NAME}_templates.Entries {
		tplt := &_${T_NAME}_templates.Entries[i]
        if (tplt.DataExcept > 0 && 0 < (tplt.DataExcept & dataVer)) {
            continue;
        }

        if (tplt.DataDiff > 0 && 0 == (tplt.DataDiff & dataVer)) {
            continue;
        }
        
		if _, ok := _${T_NAME}_table[tplt.${xmldef.get_key()}]; ok == false {
			_${T_NAME}_table[tplt.${xmldef.get_key()}] = make(${T_NAME}Map)
		}

		if skillMap, ok := _${T_NAME}_table[tplt.${xmldef.get_key()}]; ok {
			skillMap[tplt.${xmldef.get_subkey()}] = tplt
		}
	}
    
    _${T_NAME}_load = true
	return nil
}

func Find${T_NAME}Map(${xmldef.get_key(True)} ${xmldef.get_key_type()},) ${T_NAME}Map {
	if tplts, ok := _${T_NAME}_table[${xmldef.get_key(True)}]; ok {
		return tplts
	}
	return nil
}

func Find${T_NAME}(${xmldef.get_key(True)} ${xmldef.get_key_type()}, ${xmldef.get_subkey(True)} ${xmldef.get_sub_type()}) *${T_NAME} {
	if tplts, ok := _${T_NAME}_table[${xmldef.get_key(True)}]; ok {
		if tplt, exists := tplts[${xmldef.get_subkey(True)}]; exists {
			return tplt
		}
	}
	return nil
}
