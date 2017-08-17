# ReadableFormattedData

## Description
* A text data file format
* Can read json
* Can define data format ala json schema (unimplimented as of 17 August 2017)
* Doesn't require quoted strings
* Use quotes or custom string delimeters for multiline strings
* Can use either \n or , as entry delimeters

## Working Example
    id : 5
    #add_string_delimeter |
    name : |j|
    birthday : {
    	year : 1992
    	celebrations : {
    		pie : true
    	}
    }
    weakness: 2.0
    test: {yas : please, no : thank you}
    highscores : [
    	100
    	72
    	9
    	{
    		what : "test
    
    		this"
    		help : [
    			'okay', what, now, [4]
    		]
    	}, {yas : please, no : thank you}
    ]
    #remove_string_delimeter |
    
    extra : {
    #include_all another_data_object.rfd
    }


## Intended Featureset Example
    #include_definitions "./other_definitions.rfd"
    #include_members "./other_members.rfd"
    #include_macros "./other_macros.rfd"
    #include_all "./other_definitions_and_members_and_macros.rfd"
    
    @Float01: @{
    	min: 0.0
    	max: 1.0
    	type: float
    }
    @Color: @{
    	one_of: [
    		// the following two are equivalent
    		@{	type: object
    			member_types: @Float01
    			member_required_keys: [r, g, b]
    			member_optional_keys: [a]
    		},
    		{	r: @Float01
    			g: @Float01
    			b: @Float01
    			a[optional]: @Float01 1.0
    		},
    		@{	type: array
    		  element_types: @Float01
          valid_lengths: [3, 4]
    		},
    		@{	type: string
    			regex: "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8}|[A-Fa-f0-9]{3}|[A-Fa-f0-9]{4})$"
    		}
    	]
    }
    
    @ColorAnimationNodes: {
      duration: @{
        type: float
        min: 0.0
      }
      nodes : @{
        type: array
        element_types: {
          time: @Float01
          color: @Color
        }
      }
    }
    
    @black: @Color #000
    @red: @Color #f00
    
    background_color_animation: @ColorAnimationNodes [
      { time: 0.0, color: @black },
      { time: 0.0, color: @red },
      { time: 0.0, color: [1.0, 1.0, 1.0] }
    ]

## Major TODOs
* Data format schema
* Serialization of objects to text
* Serializer/Deserializer in C++
* Good error messages
