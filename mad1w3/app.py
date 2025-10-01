wrong_inputs=""" 
<!DOCTYPE html>
<html>
<head>
      <title>Something went Wrong</title>
</head>
<body>
      <h1>Wrong Inputs</h1>
      <p>somethig went wrong</p>
</body>
</html>
"""
student_details="""
<!DOCTYPE html>
<html>
<head>
      <title>Student Data</title>
</head>
<body>
      <h1>Student details</h1>
      <table style="border: 1px solid ;">
      <thead>
      <tr>
        <th> Student id </th>
        <th> Course id </th>
        <th> Marks </th>
      </tr>
      </thead>
      <tbody>
      {% for row in data %}
      <tr>
      <td>{{ row[0] }} </td>
      <td>{{ row[1] }} </td>
      <td>{{ row[2] }} </td>
      </tr>
      {% endfor %}
</body>
</html>
"""
import sys 
from Jinja2 import Template as temp