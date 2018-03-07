{% macro join_params(paramlist) %}
	{% for param in paramlist %}
		{{ param.name }}{% if not loop.last %}, {% endif %}
	{% endfor %}
{% endmacro %}

{% macro define_function(function, parent='') %}
	#### `{% if parent %}{{ parent }}.{% endif %}{{ function.name }}`
	```applescript
	{{ function.name }}({{ join_params(function.params) }})
	```
	{{ function.description }}

	{% if function.params %}
		<p class="attribute_section">Arguments</p>

		{% for param in function.params %}
			* **{{ param.name }}** {% if param.type %}[_{{ param.type }}_] {% endif %}{{ param.description }}
		{% endfor %}
	{% endif %}

	{% if function.return and (function.return.type or function.return.description) %}
		<p class="attribute_section">Returns</p>

		* {% if function.return.type %}[_{{ function.return.type }}_] {% endif %}{{ function.return.description }}
	{% endif %}

	{% if function.throwlist %}
		<p class="attribute_section">Throws</p>

		{% for throw in function.throwlist %}
			* {{ throw }}
		{% endfor %}
	{% endif %}

	{% if function.examples %}
		<p class="attribute_section">Examples</p>
		{% for example in function.examples %}

			```applescript
			{{ example }}
			```
		{% endfor %}
		<br/>
	{% endif %}
{% endmacro %}
{{ description }}

{% for class in classes %}
	# {{ class.name }}
	{{class.description }}

	{% for function in class.functions %}
		{{ define_function(function, parent=class.name) }}
	{% endfor %}
{% endfor %}


{% if functions %}
	# File level functions
{% endif %}

{% for function in functions %}
	{# {% include 'function_template.md' with context %} #}
	{{ define_function(function) }}
{% endfor %}
