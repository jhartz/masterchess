#!/usr/bin/python2.5
"""
MasterChess library - Mac OS X QuickLook generator
Copyright (C) 2012 Jake Hartz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, cgi, datetime

from MasterChess import open_database

def generate_html(mc, use_big_letters=False):
    tbl = mc.get_grand_table(full_names="db")
    
    notempty = bool(len(tbl.rows) > 1 and len(tbl.rows[0]) > 0)
    
    returning = """<!DOCTYPE html>
<html>
<head>
<style>
h1 {
    text-align: center;
    margin: auto;
}"""
    if notempty:
        returning += """
table {
    border-collapse: collapse;
}
table th, table td {
    border: 1px solid black;
    font-size: 11pt;
    padding: 6px;
    text-align: center;
}"""
    if use_big_letters:
        returning += """
p {
    font-size: 62pt;
    position: absolute;
    bottom: 0;
    right: 4%;
    text-align: right;
    opacity: .8;
    color: red;
    text-shadow: #6374AB 7px 7px 3px;
    font-weight: bold;
}
p.bigger {
    font-size: 85pt;
}"""
    returning += "\n</style>\n</head>\n<body>\n"
    
    if notempty:
        returning += "<table><thead><tr><th>&nbsp;</th>"
        for header in tbl.column_headers:
            if isinstance(header, tuple):
                header = header[1]
            returning += "<th>" + cgi.escape(header, True) + "</th>"
        returning += "</tr></thead>"
        
        returning += "<tbody>"
        for index, row in enumerate(tbl.rows):
            header = tbl.row_headers[index]
            if isinstance(header, tuple):
                header = header[1]
            returning += "<tr><th>" + cgi.escape(header, True) + "</th>"
            
            for other_index, val in enumerate(row):
                try:
                    if val == int(val):
                        val = int(val)
                except:
                    pass
                if index == len(tbl.row_headers) - 1 or other_index == len(tbl.column_headers) - 1:
                    val = "<i>" + str(val) + "</i>"
                returning += "<td>" + str(val) + "</td>"
            returning += "</tr>"
        returning += "</tbody></table>\n"
        
        matches = mc.get_matches()
        returning += "<p>"
        if use_big_letters: returning += "Matches: "
        else: returning += "Total matches: "
        returning += str(len(matches))
        if len(matches) > 0:
            latest_match = datetime.date.fromtimestamp(matches[-1].timestamp)
            if use_big_letters: returning += "<br><span>Latest: "
            else: returning += " <span style=\"float: right;\">Latest match: "
            returning += cgi.escape(latest_match.strftime("%m/%d/%y"), True) + "</span>"
        returning += "</p>\n"
    else:
        if use_big_letters:
            returning += "<p class=\"bigger\">Empty<br>database</p>\n"
        else:
            returning += "<h1>Empty MasterChess database</h1>\n"
    
    returning += "</body>\n</html>"
    return returning

if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        smallsize = False
        try:
            if sys.argv[2] == "SMALLER":
                smallsize = True
        except:
            pass
        mc_instance = open_database(path)
        if mc_instance:
            print generate_html(mc_instance, smallsize)
        else:
            print "<html><body><h1>Error</h1><p><code>An error occurred while attempting to open the database.</code></p></body></html>"