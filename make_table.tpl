%#we expect exactly two columns, one is the ID and one is the text per item
<p>{{summary}}</p>
<table border="1">
	%for row in rows:
	<tr>
	%if len(row)==2:
		<td><a href="\edit\{{row[0]}}">Item {{row[0]}}</a></td>
		<td>{{row[1]}}</td>
	%else:
		<td>bad data</td>
		<td>bad data</td>
	%end
	</tr>
%end
</table>