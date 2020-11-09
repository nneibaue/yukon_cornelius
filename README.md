# Yukon Cornelius Web Scraper


This library provides a small, easy-to-use web scraping framework in Python. The workflow is modeled after mining, and is aptly named after [Yukon Cornelius](https://rankinbass.fandom.com/wiki/Yukon_Cornelius) - The Greatest Prospector in the North - and provides building blocks for scraping items of interest from websites and web pages. Included in this library are two pre-configured sample websites (a classic cars forum and a local html page also used for testing purposes) that provide examples for how to implement the framework. 

## Author's Note

The following questions were presented:
 1. Have you thought about the modularity, maintainability, testability, and shareability of your code? 
 2. Is your code a one-off script or could it be used as the basis of a more general scraping engine? 
 3. Is your code written in good, idiomatic Python? 
 
This submission is an attempt to create a general scraping engine, as noted in question #2. After completing about 75% of the *one-off script* approach, I decided I would take on the challenge of creating something a bit more robust and generalizable. It was indeed a challenging problem, especially given my lack of experience getting into the weeds with html documents, but I am satisfied with this project. 

The specific challenge I attempted to take here was an answer to the following:

> Given that website designs are incredibly varied and unique, How do I create a scraping framework that allows full website-specific customization with *minimal implementation code* for new websites. 

My solution, as I hope to persuade you, solves this problem quite cleanly, while addressing scalability (via parallelization) in addition to the aforementioned modularity, maintainability, testability, and shareability. I am confident that I could implement a variety of different sites using this framework with minimal headache.



## Quickstart
The software can be run out of the box with the following two steps
1. Activate the environment
2. Run `mine.py`

### Activating the environment
The zip file included a local environment `env` with required installed packages. Activate it by executing the following command:

    source env/bin/activate
  
Your terminal prompt should now be prepended with `(env)`, e.g. `(env) computer:~ user$ `

<br>

### Running `mine.py`
As mentioned above, there are two samples already configured for mining. These can be mined via the following command:

    python mine.py <website_name>

Valid website names are shown in `config.json`. To run the classic cars website, run:

    python mine.py classic_cars_forum
    
This will mine the classic cars website and save csv data in *exports/classic_cars_forum.csv*. Mining can also be done with a yaml config file. An example of this is shown in *run_configs/run1.yml*, and it can be run in the same way via:

    python mine.py run_configs/run1.yml
    
<br>

## Design Summary and Walkthrough
As mentioned above, this design is inspired by a mining analogy. Each website has a dedicated `Prospector` that walks through the site collecting `Ore` objects that correspond to certain configurable criteria and placing them into an `ore_cart`. The `Ore` is optionally processed by the `Prospector` as it enters the `ore_cart`, and is later refined into a given data type. At this point, `Ore` can be refined into *csv*, *json*, or *html* tabular data.  

<br>

### ProspectorBase and Ore
This is where the magic happens. The `ProspectorBase` defines the logic for mining a page according to specific rules that must be defined in subclasses. This is explained in futher detail below. `Ore` is essentially a dictionary wrapper that contains a few additional features helpful to the mining and refining processes, and will only be instantiated by prospectors when mining.

All prospectors have access to a dynamic `state` attribute that keeps track of the current mining progress and contains a mixture of read-only and read/write attributes. Some of these attributes are useful when implementing page turning logic (explained below). Furthermore, additional constants for specific classes can be defined in `yukon_cornelius.constants` using the same class name.


New prospectors can be easily implemented via the following steps:
  
  #### Step 1
Define a new website in *website_config.json* using the required keys listed in `yukon_cornelius.consants.REQUIRED_CONFIG_KEYS`. Let's take the classic cars example:

```json
  "classic_cars_forum": {
    "source": "https://www.oldclassiccar.co.uk/forum/phpbb/phpBB2/viewtopic.php?t=12591",
    "source_type": "https_url",
    "prospector_class": "ClassicCars",
    "attributes": [
      "id",
      "name",
      "date",
      "body"
    ]
  }
```

> `source` : Must be a valid form of the source type below

> `source_type` : Must be one of the valid source types defined in `yukon_cornelius.constants.VALID_SOURCE_TYPES`

> `prospector_class` : Name of class to be implemented in `yukon_cornelius.prospectors.sites`. This will be explained in the next step.

> `attributes` : Attributes of interest. These values eventually translate to column names in the final tabular data, and define which methods need to be overloaded in the `prospector_class`

#### Step 2
Implement the class defined by the `prospector_class` field. This class must implement *tester* methods for each of the attributes defined by the `attributes` field above that take on the form `_is_<attribute>_tag`. These methods must accept a beautiful soup tag and return a boolean. Any attribute that is listed in the config but not implemented will raise an exception. For the classic cars example above, a `ClassicCars` implementation would look like the following:

```python
class ClassicCars:
  def _is_id_tag(self, tag):
    # Check things
    return <True | False>
  
  def _is_name_tag(self, tag):
    # Cehck things
    return <True | False>
    
  def _is_date_tag(self, tag):
    # Check things
    return <True | False>
  
  def _is_body_tag(self, tag):
    # Check things
    return <True | False>
 
```

The only responsibility of these methods is to check whether or not `tag` contains the desired attribute. By default, if these methods return True, then that tag is stringified and placed in the prospectors ore_cart; hoewever, this process can be intercepted by a processing method that takes on the form `_process_<attribute>`. For example, if we wanted to not only find the date-containing tags, but also process them, we would implement a method like this:

```python

  def _process_date(self, tag):
    # Extract information from the tag
    return <string>
``` 

In addition to attribute testing and processing, prospectors must implement the `_is_forum_end` method to determine when to stop mining. Optionally, there is also a `_turn_page` method that can be implemented to process page turns for multi-page sites. In the *classic cars* example, this is implemented by modifying the 'current_source' state variable. The full implementation for *classic cars* can be found inside the code at `yukon_cornelius.prospectors.sites`.

## Design Analysis

### Strengths
- Full customization. Because tags are searched individually and processed separately, the user could theoretically mine *any* text from *any* website
- Robust error handling. There is a rigorous structure in place forcing the user to "stay within the lines" when subclassing and building configuration files.
- Parts included. All of the plumbing remains intact when implementing a new website.

### Weaknesses
- Complex. In order to satisfy the requirement of *easy to implement a new website*, the `ProspectorBase` and `Ore` classes rely heavily on "magic" methods, such as `getattr`, `hasattr`, and `setattr`, sacrificing some readability in favor of flexibility. 



## Configuring a run
Run configs currently support running one or more configured websites in parallel. In the example above, we used the *run1.yml* configuration file, which contains the following:

```
websites:
    classic_cars_forum:
        filetype: csv

    sample_forum:
        filetype: json
```

Each website listed above corresponds to a site name from *website_config.json* and specifies a filetype for data export. Current valid filetypes can be found under `constants.VALID_ORE_EXPORT_TYPES.` 
