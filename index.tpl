<p>flaschenpost</p>

<p>{{summary}}</p>

<p><a href="/todo">show all open entries</a></p>
<p><a href="/new">create new entry</a></p>
<p><a href="/help">help</a></p>
<p><a href="/logout">logout</a></p>

<p>Available users:</p>
<table border="1">
%for row in rows:
	<tr>
		<td>{{row[0]}}</td>
		<td><a href="/todo/{{row[0]}}">show entries</a></td>
	</tr>
%end
</table>
