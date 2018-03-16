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
)

type ${T_NAME}Vec []${T_NAME}

type ${T_NAME}s struct {
	XMLName xml.Name        `xml:"g_${T_NAME}"`
	Entries []${T_NAME} `xml:"entry"`
}

type ${T_NAME} struct {
    DataExcept      uint32      `xml:"nDataExcept"`         // version except flags
    DataDiff        uint32      `xml:"nDataDiff"`           // version differentiation flags
% for field in fields:
    ${xmldef.get_fname(field,True)}        ${xmldef.get_ftype(field)}      `xml:"${xmldef.get_fname(field)}"`       // ${xmldef.get_fcomment(field)}
% endfor
}

// Load ${T_NAME}(s) from xml template.
func Load${T_NAME}(xmlfile string, dataVer uint32) error {
	content, err := ioutil.ReadFile(xmlfile)
	if err != nil {
		return err
	}

	root := bytes.Index(content, []byte("<"+_${T_NAME}s_root+">"))
	rootEnd := bytes.Index(content, []byte("</"+_${T_NAME}s_root+">"))
    err = xml.Unmarshal(
		content[root:rootEnd+3+len(_${T_NAME}s_root)],
		&_${T_NAME}_templates)
    if err != nil {
		return err
	}
    
    var tmps  ${T_NAME}Vec
    for i, _ := range _${T_NAME}_templates.Entries {
        tplt := &_${T_NAME}_templates.Entries[i]
        if (tplt.DataExcept > 0 && 0 < (tplt.DataExcept & dataVer)) {
            continue;
        }

        if (tplt.DataDiff > 0 && 0 == (tplt.DataDiff & dataVer)) {
            continue;
        }
        
        tmps = append(tmps, *tplt)
    }
    
    _${T_NAME}_templates.Entries = tmps
    return nil
}

func Get${T_NAME}Vec() ${T_NAME}Vec {
	return _${T_NAME}_templates.Entries
}
