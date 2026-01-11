When using Mapbox GL JS, there are several ways to add your own data to the map. The right approach depends on the type, quantity, and style of data you want to display.

The most important distinction is whether you want to display data above the map or within the map itself, as each approach has fundamental differences in how the data is loaded, styled and interacted with.

For most use cases where you want to add point data to your map, Markers provide the quickest and easiest solution.
Above the Map: Default Markers
Default pin-style markers with custom colors - the quickest way to add point data.
Above the Map: Custom Markers
HTML elements pinned to a map location, using a custom SVG image
In the Map: Style Layers
Style layers are rendered as part of the map itself, allowing for high-performance visualization of large datasets, and positioning relative to other map features.
Understanding how the Map is rendered

Mapbox GL JS maps are rendered entirely in the browser using WebGL technology, which enables high-performance, smooth rendering of complex geographic data in a <canvas> element.

The map you see is not a single image, but rather a composite of many virtual layers. The SDK fetches data for roads, buildings, and other map features from Mapbox servers, assembles these layers in memory, and presents them based on the current map position, zoom level, and style. In Mapbox GL JS, this rendering is handled by the Map class.

This client-side rendering enables smooth interactions with the map - you can rotate, tilt, and zoom while maintaining crisp visuals at any scale. The Map instance dynamically loads additional data as needed based on the current view.

Understanding this architecture is key to choosing how to add your data: you can either add visual elements above the map using DOM elements rendered in the browser's UI layer (markers) or integrate your data into the map itself as additional layers that can be mixed into the existing layer stack (style layers).
Above the Map: Markers
Markers are rendered above the map by the browser's DOM layer, and are fixed to a geographic location so they will move when the map moves.
In the Map: Style Layers
Style layers are rendered as part of the map itself, allowing for high-performance visualization of large datasets, and positioning relative to other map features.
Choosing the right approach

When deciding how to add your data to the map, consider the following factors:

    The complexity of your data
    The level of interactivity you need
    Performance requirements
    Development time and effort

Markers provide the quickest way to visualize point data. Style layers offer maximum flexibility and performance for complex datasets, including points, lines, or polygons.
Markers

Markers are DOM elements positioned above the map at specific geographic coordinates. They provide a quick way to add interactive elements with minimal code.

Advantages:

    Easy to implement with standard web development skills
    Default SVG marker icon, ability to control size and color via options
    Full HTML/CSS customization
    Built-in drag and drop support
    Easy interaction handling with DOM events

Limitations:

    Less efficient for large datasets (100+ markers)
    Limited interaction with other map features
    No built-in clustering support

Style Layers

Style layers are additional layers rendered as part of the map, integrated along with the roads, buildings, and other map features — sources provide the geographic data (GeoJSON, vector tiles, raster tiles), and layers define how that data is styled (circle, fill, line, symbol, heatmap, etc.).

They are ideal for large or complex datasets, advanced styling, or when you need precise control over map rendering.

Advantages:

    Maximum flexibility and performance — can handle tens of thousands of features.
    Compatible with vector tiles for large datasets with wide geographic coverage.
    Can make style changes dynamically without reloading the data.
    Can use data-driven styling (styles change based on feature properties).

Limitations:

    More verbose to set up, requires familiarity with the Mapbox Style Specification.
    Requires data in specific formats, such as GeoJSON or vector tiles.
    Complex integration for user interaction — you'll need to add event listeners and query rendered features 


When using Mapbox GL JS, Style Layers provide a way to display many features on a map from vector or geojson sources. In contrast to Markers, which are HTML elements positioned above the map, Style Layers are rendered directly within the map canvas using WebGL.

Style layers provide a more efficient and performant way to display many features on a map. They can display points, lines, and polygons and offer several options for importing, styling, and interacting with your data.
Style Layers
After your data as a vector or geojson source, you can add a style layer to visualize it on the map.

Benefits:

    Style Layers are more efficient and performant, especially when dealing with a large number of features on the map from vector or geojson sources.
    Style Layers offer extensive customization options, allowing developers to precisely control the appearance of map elements. This includes options such as the color, opacity, size and many other visual attributes listed in the Layers section of the Mapbox Style Spec.

Limitations:

    Data must be prepared as a hosted vector tileset or valid GeoJSON data.
    Style Layers require a developer to learn specific Mapbox APIs and usage patterns associated with Layers. In contrast, Markers use higher-level abstractions.
    Using the lower-level APIs of Style Layers may take more time, especially if you are new to Mapbox GL JS or mapping technologies.
    To achieve more sophisticated data-driven styling, developers will need to learn how to use Mapbox Expressions to control the appearance of map features based on the underlying data. This adds complexity to the development process.

This guide covers the basics of adding your own data to a map using sources and layers. To learn more about working with sources and layers, see the full guide:
RELATED
Map styles: Work with sources and layers

See the full guide on working with sources and layers in Mapbox GL JS.
Add your data as a source

Before you can add a Style Layer, you need to add a data source to the map. Sources provide the geographic data that the Style Layer will render. The most commonly used source types are vector and geojson sources, each requiring different data formats and handling.

Both vector and geojson sources are added using the Map.addSource method.
vector sources

Vector sources retrieve data from a server in the form of vector tiles, or chunks of geographic data representing small areas of the earth's surface. Using vector tiles means you don't have to load all the data at once, which is ideal for large datasets that cover wide geographic areas.

To add your own data as a vector source, you must first process the data into a vector tileset. There are several options available for creating and hosting vector tilesets:

    Use Mapbox's Data manager to upload data and generate vector tiles using an intuitive graphical user interface.
    Use Mapbox Tiling Service (MTS) to build a data pipeline for continuous updates to a vector tileset from source data.
    Use third party tools to create vector tiles from your source data and host them on your own infrastructure.

Add a Mapbox-hosted vector source

Vector tilesets hosted on your Mapbox account are accessible using the tileset URL following the format mapbox://username.tilesetid.

The following snippet shows how to add a Mapbox-hosted vector source:

map.addSource('vector-source', {
  'type': 'vector',
  'url': 'mapbox://your-tileset-id'
});

// now you can add a layer to use this source

EXAMPLE
Add a vector tile source

See an interactive example showing how to add a Mapbox-hosted vector tile source to a map.
Add a third-party vector source

You can also add vector sources hosted by third-party providers or on your own infrastructure. To do this, you need to provide the URL template for the vector tiles, which typically includes placeholders for the zoom level ({z}), x-coordinate ({x}), and y-coordinate ({y}) of the tile.

map.addSource('third-party-vector-source', {
  'type': 'vector',
  'url': 'https://{s}.example.com/tiles/{z}/{x}/{y}.pbf'
});

EXAMPLE
Add a third party vector tile source

See an interactive example showing how to add a third party vector tile source to a map.
geojson sources

geojson sources contain the same type of data as vector sources, but the data is loaded from a GeoJSON object or URL. This allows for more flexibility as developers can change and host GeoJSON data without needing to regenerate and serve vector tiles.

A limitation of geojson sources is that they may not perform as well as vector tiles when rendering large datasets, as the entire dataset must be added to the map at once regardless of what features are visible on the map's current location and zoom level.

Developers will often source data from a custom API endpoint that serves GeoJSON data live from a database, or they may use static GeoJSON files hosted on the web or bundled with their app.
Add a geojson source from a URL

addSource accepts a URL to a GeoJSON file, which can be hosted on your own server or a third-party service. Mapbox GL JS will fetch the data from the URL behind the scenes and create a source from it.

map.addSource('geojson-source', {
  'type': 'geojson',
  'data': 'https://example.com/data.geojson'
});

// now you can add a layer to use this source

Add a geojson source from a local file

You can store geojson files alongside your HTML, CSS, and JavaScript files in your project and load them using a relative URL. Note that this approach requires the site and its files to be served from a web server, as most browsers block fetching local files due to security restrictions.

map.addSource('geojson-source', {
  'type': 'geojson',
  'data': './path-to-my-geojson-file.geojson'
});

// now you can add a layer to use this source

If you are using a bundler, you may be able to import a GeoJSON file at the top of your JavaScript file, making it available as a JavaScript object.

import someGeojsonData from './path-to-my-geojson-file.geojson' assert { type: 'json' };

map.addSource('geojson-source', {
  'type': 'geojson',
  'data': data
});

// now you can add a layer to use this source

Add a geojson source from inline data

You can define a GeoJSON object directly in your JavaScript code and use it as the data for a geojson source. This is useful for small or static datasets or when you want to quickly test with sample data.

const myGeojsonData = {
    'type': 'FeatureCollection',
    'features': [
      {
        'type': 'Feature',
        'geometry': {
          'type': 'Point',
          'coordinates': [-74.0060, 40.7128]
        },
        'properties': {
          'title': 'New York City'
        }
      },
      ... // more features here
    ]
  }

map.addSource('geojson-source', {
  'type': 'geojson',
  'data': myGeojsonData
});

// now you can add a layer to use this source

Other source types

For a complete list of source types supported by Mapbox GL JS, see the Sources guide or consult the references listed below.
RELATED
Sources API reference

API reference documentation for adding sources using Mapbox GL JS.
RELATED
Mapbox Style Specification - Sources

View the reference docs for the Mapbox Style Specification to see details about each source type and its properties.
Add layers that use your data sources

Once you have added a source to the map, you can add a Style Layer that uses that source to render features on the map.

For example, you can create a circle layer to represent point data as circles on the map, or a symbol layer to display icons or text. The following snippet shows how to add a circle layer and a symbol layer that uses a common source:

// a vector or geojson source with id "my-pointdata-source" must have been added to the map

// add a circle layer
map.addLayer({
  'id': 'circle-layer',
  'type': 'circle',
  'source': 'my-pointdata-source',
  'paint': {
    'circle-radius': 6,
    'circle-color': '#007cbf'
  }
});

// add a symbol layer
map.addLayer({
  'id': 'symbol-layer',
  'type': 'symbol',
  'source': 'my-pointdata-source',
  'layout': {
    'icon-image': 'my-icon',
    'icon-size': 1.5
  }
});

Layer Types for vector and geojson sources

Layer types are defined in the Mapbox Style Specification and are used to render different types of data on the map. The most common layer types for showing data from vector and geojson sources are:

    Circle Layer: This layer is used to represent point data as circles on the map, useful for visualizing locations with minimal code and configuration.

A popup attached to a marker on a map
EXAMPLE
Circle Layer Example

See an interactive example showing how to add a GeoJSON source to a map and visualize it using a circle layer.

    Line Layer: This layer is used to render lines on the map, often used to show routes, directions or paths.

A popup attached to a marker on a map
EXAMPLE
Line Layer Example

See an interactive example showing how to add a GeoJSON source to a map and visualize it using a line layer.

    Fill Layer: This layer is used to fill a polygon with a color.

A popup attached to a marker on a map
EXAMPLE
Fill Layer Example

See an interactive example showing how to add a GeoJSON source to a map and visualize it using a fill layer.

    Symbol Layer: This layer is used to render icons or text representing point locations on the map.

A popup attached to a marker on a map
EXAMPLE
Symbol layer example

See an interactive example showing how to add a GeoJSON source to a map and represent it using symbol layers to show glyphs and text.

The layers each have their own set of properties and styling options, allowing you to customize the appearance of the map features. For example, you can set the color, opacity, size, and other visual attributes of each layer type.

For details and code snippets about all available layer types, see the Layers guide, or browse the examples below.

Each layer must specify a data source, which defines the geographic data that a layer will render.
Adding interactivity to layers

You can add click and hover events to layers to make them interactive:

// assume a layer with id "airport" has been added to the map

map.addInteraction('click', {
    type: 'click',
    target: { layerId: 'airport' },
    handler: ({ feature }) => {
        console.log('Clicked on airport:', feature.properties);
        // handle the click event, e.g., show a popup or highlight the feature
    }
});

EXAMPLE
Add feature-level interactions to a map

Learn how to add click and hover interactions to a layer on the map.
GUIDE
User Interactions Guide

See the Interactions API Guide for more details on interacting with features on the map.
Data-driven styling

Use expressions to style features based on their properties. It is also possible to style features based on zoom level, allowing for dynamic visualizations that change as users zoom in and out.
A map showing circles of varying sizes and colors representing earthquake data.

map.addLayer({
  'id': 'data-driven-circles',
  'type': 'circle',
  'source': 'my-geojson-source',
  'paint': {
    // make circles larger based on a 'mag' property
    'circle-radius': [
      'interpolate',
      ['linear'],
      ['get', 'mag'],
      1, 8,
      1.5, 10,
      2, 12,
      2.5, 14,
      3, 16,
      3.5, 18,
      4.5, 20,
      6.5, 22,
      8.5, 24,
      10.5, 26
    ],
    // color circles based on a 'mag' property
    'circle-color': [
      'interpolate',
      ['linear'],
      ['get', 'mag'],
      1, '#fff7ec',
      1.5, '#fee8c8',
      2, '#fdd49e',
      2.5, '#fdbb84',
      3, '#fc8d59',
      3.5, '#ef6548',
      4.5, '#d7301f',
      6.5, '#b30000',
      8.5, '#7f0000',
      10.5, '#000'
    ],
    'circle-stroke-color': 'white',
    'circle-stroke-width': 1,
    'circle-opacity': 0.6
  }
});

EXAMPLE
Style circles with a data-driven property

Learn how to style circle layers based on a data property using expressions.
EXAMPLE
Change building color based on zoom level

Learn how to style building layers based on the zoom level using expressions.
Other layer types

Other layer types are possible, including raster tile layers, images, videos, and custom types. For a complete list of layer types supported by Mapbox GL JS, see the Layers guide or consult the references listed below.
RELATED
Layers API reference

API reference documentation for adding style layers using Mapbox GL JS.
RELATED
Mapbox Style Specification - Layers

View the reference docs for the Mapbox Style Specification to see details about each layer type and its properties.
Add your data to a custom style in Mapbox Studio

The concepts outlined above involve coding to add sources and layers to the map at runtime after the initial map style has been loaded. Using Mapbox Studio, you can create a custom style that combines your data sources and layers with basemap layers provided by Mapbox.

Adding your data to a custom style requires vector sources (GeoJSON sources are not supported in Mapbox Studio) and allows you to load the map in your application with your data already included and styled, simplifying your runtime code.

See our tutorials for more information on creating custom styles:
RELATED
Getting started with Mapbox Standard in Studio

This tutorial will walk you through the process of adding custom data to a style that uses the Mapbox Standard basemap.

Set a style
On this page

    Load a style
        Mapbox Standard
        Custom styles
        Delay setting the style
    Configure a style
        Mapbox Standard
        Custom styles
    Change to a different style (#change-to-a-different-style)

When adding a map to a web application or website using Mapbox GL JS, the map's style dictates the visual design of the map, including colors, labels, and feature visibility. It also includes information about data sources, and is used by the SDK to fetch the appropriate data necessary to render the map.
A map using the Mapbox Standard style.
A map using the Mapbox Outdoors style.
A map using the Mapbox Satellite style with 3D terrain.

By default Mapbox GL JS uses the Mapbox Standard style, which is a versatile and visually appealing map style suitable for many applications. Mapbox Standard offers many configuration options, allowing developers to customize the map's appearance to suit the needs of their application. If a completely unique look and feel is needed for the map, developers can create custom styles using Mapbox Studio, which can then be loaded into the map.

Once a style is loaded, you can continue to manipulate it at runtime, changing the appearance of the map by changing style configurations, adding or removing layers, changing layer properties, and more. This guide explains how to set and configure a style when initializing a map and how to switch styles dynamically during runtime.
Load a style

Mapbox GL JS provides an embeddable map interface using the Map class. To render a map you will need to determine which style the renderer should use. You can rely on the Mapbox Standard style which is loaded by default, or you can specify another style.
Mapbox Standard

Mapbox Standard is our general-purpose map style that is designed to be used in a wide range of applications. It is suitable for most use cases and includes a variety of configuration options to customize the map's appearance.

Mapbox Standard is the default style, and instantiating a Map without specifying any style means your map will use Mapbox Standard.

// if the `style` option is not specified, loads Mapbox Standard by default
const map = new mapboxgl.Map({
    container: 'map',
})

You can explicitly set Mapbox Standard as the style for your map by adding its style URL to the style option when initializing the map:

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/standard',
})

Custom styles

You can also create your own custom styles using the Mapbox Studio style editor. Custom styles can be used to create a unique look and feel for your map, tailored to your application's design needs. You can use Mapbox Standard edited in Mapbox Studio or any other style as a base—or start from scratch entirely. Learn how to customize Standard in this tutorial, how to build a style from scratch in this guide or explore our style gallery.

You can specify a style to use when you instantiate a map using a Style URL or a Style JSON string.
Load a style using a Style URL

All Mapbox styles and custom styles created in Mapbox Studio have a unique style URL starting with mapbox://. You can use this URL to load a style when initializing a map.

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/your-mapbox-username/your-custom-style-url',
})

Loading a Style using Style JSON
Though less common, you can also load a style from a JSON string, either loaded from a local file or downloaded over the network. See a minimal style JSON example in Delay setting the style below.
Delay setting the style

If you want to initialize the Map but delay loading a style until after it is displayed on the UI, you can set the style option to an empty style JSON when initializing the map. This will display the map with a white background until you add a style later using the setStyle method.

const map = new mapboxgl.Map({
    container: 'map',
    style: {
        version: 8,
        sources: {},
        layers: []
    },
})

In the case above, the map is rendered with solid white background color by default. But, if you want to adjust the color of the map's background to fit your design before your style is loaded to the Map, you can create a minimal style JSON string with a background layer set to the desired color.

const map = new mapboxgl.Map({
    container: 'map',
    style: {
        version: 8,
        sources: {},
        layers: [
            {
                id: 'background',
                type: 'background',
                paint: {
                    'background-color': 'hsl(100, 50%, 50%)',
                },
            },
        ],
    },
})

Configure a style

Depending on which map style you choose, you have different configuration options available to customize aspects of your style such as fonts, colors, and more.
Mapbox Standard

Mapbox Standard and Mapbox Standard Satellite are our default, all-purpose map styles, and are recommended for most use cases. Mapbox Standard and Mapbox Standard Satellite provide a limited set of configurations instead of allowing for full manipulation of the style.

Each style can be configured with several options, including light presets, label visibility, feature visibility, color theming, and fonts, and more. You can set these at runtime using the setStyle method.
PLAYGROUND
Mapbox Standard Style Playground

Using this interactive tool, you can see in real-time how different configuration options affect the Mapbox Standard or Mapbox Standard Satellite styles.

All configuration properties for Mapbox Standard are also available for Mapbox Standard Satellite except for toggling 3D objects and color theming. To learn more about configuration options, refer to the Mapbox Standard Guide and the Mapbox Standard API Reference Docs.

The following sample code shows how to change the 3D lights from the default preset, day, to another preset, dusk, by setting the lightPreset property. The code also shows how to hide the point of interest labels by setting the showPointOfInterestLabels property to false. You can set these properties either when initializing the map with the config parameter or after the map has been initialized using the setConfigProperty method. To update the configuration you must specify the import id of the style you want to configure. For Mapbox Standard, this is basemap.

// configure Mapbox Standard during map initialization
const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/standard',
    config: {
        basemap: {
            lightPreset: 'dusk',
            showPointOfInterestLabels: false,
        }
    }
});

// configure Mapbox Standard after map initialization
map.setConfigProperty('basemap', 'lightPreset', 'dusk');

map.setConfigProperty('basemap', 'showPointOfInterestLabels', false);

All configurations are also available in Mapbox Studio, where you can create a custom style that imports Mapbox Standard or Mapbox Standard Satellite and adjust the configurations as needed.
Custom styles

Custom styles can be configured by calling methods to update the properties of the style. The most common configurations are updates to layer properties, such as changing the color of a line or the visibility of a label.

For example, you may want to hide an existing layer by setting its visibility to none using setLayoutProperty, or change the color of a fill layer by setting its fill-color property using setPaintProperty. Learn more about updating layers in the Work with sources and layers guide.

// hide the point of interest labels layer
map.setLayoutProperty('poi-label', 'visibility', 'none');

// set the fill color of the water layer to a teal color
map.setPaintProperty('water', 'fill-color', '#45d9ca');

This approach requires knowing the ids and types of layers in the style and understanding the properties that can be updated for each layer type. You can explore the properties available for a given layer type in the Mapbox Style Specification.

An alternative approach to adding many runtime configuration changes for a style is to create a custom style in Mapbox Studio. You can make the desired changes in the style editor and load the custom style in your application.
Change to a different style (#change-to-a-different-style)

You can change the style any time after initializing the map using the setStyle method.

// load the Mapbox Standard Satellite style, replacing the current map style
map.setStyle('mapbox://styles/mapbox/standard-satellite');

If you added any layers after map initialized, you will need to re-add them after the new style is loaded.

Work with sources and layers
On this page

    Add and update layers
        Add a layer at runtime
        Update a layer at runtime
        Specify order of a layer at runtime for Mapbox Standard
        Specify order of a layer at runtime for other styles
        Remove a layer at runtime
    Source types
        Vector
        GeoJSON
        Raster
        Raster DEM
        Image
    Layer types
        Fill layer
        Line layer
        Symbol layer
        Circle layer
        Fill extrusion layer
        Hillshade layer
        Heatmap layer
        Raster layer
        Background layer

Layers define how map features—such as roads, buildings, water, and points of interest—are visually represented in a Mapbox style. Each layer handles rendering specific data from a source, determining its appearance and behavior on the map. With Mapbox GL JS, developers can dynamically add, remove, and change layers to customize their map's design and functionality.

This guide covers the fundamentals of working with layers, including:

    The relationship between sources and layers
    Adding and updating layers at runtime
    Controlling layer order and rendering behavior
    Using different layer types (such as fill, line, symbol, and raster layers)
    Understanding layers is essential for customizing a Mapbox-powered map and displaying data in a visually meaningful way.

Add and update layers

You can use Mapbox GL JS API to add more styled data to the map at runtime. There are two key concepts to understand when preparing to add a layer to a style at runtime: layers and sources.

Sources contain geographic data. They determine the shape of the features you’re adding to the map and where in the world they belong.

Layers contain styling information. They determine how the data in a source should look on the map.

A layer is a styled representation of data of a single type (for example polygons, lines, or points) that make up a map style. For example, roads, city labels, and rivers would be three separate layers in a map. There are several layer types (for example fill, line, and symbol). You can read more about layers in the Mapbox Style Specification.

Most layers also require a source. The source provides map data that Mapbox GL JS can use with a style document to render a visual representation of that data. There are several source types (for example vector tilesets, GeoJSON, and raster data). You can read more about sources in the Mapbox Style Specification.

In Mapbox GL JS, the Map class exposes the entry point for all methods related to the style object including sources and layers.
Add a layer at runtime

To add a new layer to the map at runtime, start by adding a source using the Style’s addSource method. It is important that you add the source for a new layer after the map has loaded but before attempting to add the layer itself because the source is a required parameter for most layer types.

Then, you’ll use the addLayer method to add the layer to the style. When adding the style layer, you will specify:

    A unique id that you assign to the new layer
    The layer type (for example fill, line, or symbol)
    What data to use by referencing a source
    The appearance of the data by setting various properties (for example color, opacity, and language)

The sample code below illustrates how to add a GeoJSON source and then add and style a line layer that uses the data in that source.

map.on('style.load', () => {
  map.addSource('route', {
    type: 'geojson',
    data: {
      /* ... GeoJSON data ... */
    }
  });
  map.addLayer({
    id: 'route',
    type: 'line',
    source: 'route',
    paint: {
      'line-color': '#888',
      'line-width': 8
    }
  });
});

The exact available properties available when adding a source and layer varies by source type and layer type. Read more about source types and layer types below.
Update a layer at runtime

You can also update the style of any layer at runtime using the layer's unique layer ID and defining style properties. The sample code below illustrates how to get an existing layer by referencing a layer ID and updating the line-opacity value.

map.setPaintProperty('route', 'line-opacity', 0.9);

The exact available properties available when updating a layer varies by layer type. Read more about layer types below.
Specify order of a layer at runtime for Mapbox Standard

Mapbox Standard and Standard Satellite uses the slot property to specify where custom data layers can be added. Slots are predetermined locations in the Standard basemap where your layer can be inserted. To add custom layers in the appropriate location in the Standard basemap layer stack, Standard offers 3 carefully designed slots that you can leverage to place your layer. These slots will stay stable, and you can be sure that your own map won't break even as the basemap updates over time.
Slot	Description
bottom	Above polygons (land, landuse, water, etc.)
middle	Above lines (roads, etc.) and behind 3D buildings
top	Above POI labels and behind Place and Transit labels
not specified	Above all existing layers in the style

Here’s an example of how to assign a slot to a layer:

map.addLayer({ type: 'line', slot: 'middle' /* ... */ });

Make sure to use slot instead of layer id when inserting a custom layer into the Standard basemap. Layers within the same slot can be rearranged using the optional beforeId argument. This argument specifies the id of an existing layer before which the new layer will be inserted, causing the new layer to appear visually underneath the specified layer. But, if the layers are in different slots, the beforeId argument is ignored, and the new layer is added to the end of the layers array.
Slots and performance-optimized layers reordering

During 3D globe and terrain rendering, GL JS aims to batch multiple layers together for optimal performance. This process might lead to a rearrangement of layers. Layers draped over globe and terrain, such as fill, line, background, hillshade, and raster, are rendered first. These layers are rendered underneath symbols, regardless of whether they are placed in the middle or top slots or without a designated slot.
EXAMPLE
Layer slot example

Add a new layer to a slot in the Mapbox Standard Style.
Specify order of a layer at runtime for other styles

Map styles contain many individual layers (for example roads, buildings, labels, and more). By default, when you add a new layer to the style, it is placed on top of all the other layers. You can specify where the new layer is positioned relative to existing layers with an additional argument to the addLayer method which specifies an existing layer below which the new one should go.

map.addLayer({ type: 'line' /* ... */ }, 'state-labels');

Remove a layer at runtime

You can remove a layer from a style using Style's removeLayer method.

map.removeLayer('route');

Source types
Vector

A vector source, VectorTileSource, is a vector tileset that conforms to the Mapbox Vector Tile format. A vector source contains geographic features (and their data properties) that have already been tiled. Learn more about the benefits of vector tilesets and how they work in the Vector tiles documentation. For vector tiles hosted by Mapbox, the "url" value should be of the form of mapbox://username.tilesetid.

map.addSource('terrain', {
  type: 'vector',
  url: 'mapbox://mapbox.mapbox-terrain-v2'
});

Note

All style layers that use a vector source must specify a "source-layer" value.
GeoJSON

A GeoJSON source, GeoJSONSource, is data in the form of a JSON object that conforms to the GeoJSON specification. A GeoJSON source is a collection of one or more geographic features, which may be points, lines, and polygons. Data must be provided via a "data" property, whose value can be a URL or inline GeoJSON.

map.addSource('polygon', {
  type: 'geojson',
  data: { type: 'Feature', geometry: { type: 'Polygon' /* ... */ } }
});

EXAMPLE
Add a polygon to a map using a GeoJSON source

See the format of the data used in the sample code above in the GeoJSON polygon example.
Raster

A raster source, RasterTileSource, is a raster tileset. For raster tiles hosted by Mapbox, the "url" value should be of the form mapbox://tilesetid.

map.addSource('openstreetmap', {
  type: 'raster',
  tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
  tileSize: 256,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
});

Raster DEM

A raster DEM source, which is a special case of RasterTileSource, contains elevation data and refers to Mapbox Terrain-DEM (mapbox://mapbox.mapbox-terrain-dem-v1), which is the only supported raster DEM source. It must be added with the type: "raster-dem.

map.addSource('dem', {
  type: 'raster-dem',
  url: 'mapbox://mapbox.mapbox-terrain-dem-v1'
});

Image

An image source, ImageSource, is an image that you supply along with geographic coordinates. Specify geographic coordinates in the "coordinates" array as [longitude, latitude] pairs so the map knows at what location in the world to place the image. Each coordinate pair in the "coordinates" array represents the image corners listed in clockwise order: top left, top right, bottom right, bottom left.

map.addSource('radar', {
  type: 'image',
  url: '/mapbox-gl-js/assets/radar.gif',
  coordinates: [
    [-80.425, 46.437],
    [-71.516, 46.437],
    [-71.516, 37.936],
    [-80.425, 37.936]
  ]
});

Layer types
Fill layer

A fill style layer renders one or more filled (and optionally stroked) polygons on a map. You can use a fill layer to configure the visual appearance of polygon or multipolygon features.
Fill layer

To add a fill layer, you need to first add a vector or GeoJSON source that contains polygon data. Then you can use the available properties in fill layer to customize its appearance (for example, the color, opacity, or pattern).

map.addLayer({
  id: 'maine',
  type: 'fill',
  source: 'maine',
  paint: {
    'fill-color': '#0080ff',
    'fill-opacity': 0.5
  }
});

EXAMPLE
Fill layer example

Add a polygon to a map with an optional stroked border using a GeoJSON source.
Line layer

A line style layer renders one or more stroked polylines on the map. You can use a line layer to configure the visual appearance of polyline or multipolyline features.
Line layer

To add a line layer, you need to first add a vector or GeoJSON source that contains line data. Then you can use the available properties in line layer to customize the appearance of the layer (for example, the color, width, or dash pattern).

map.addLayer({
  id: 'route',
  type: 'line',
  source: 'route',
  layout: {
    'line-cap': 'round'
  },
  paint: {
    'line-color': 'red',
    'line-opacity': 0.8
  }
});

EXAMPLE
Line layer example

Add a line to a map using a GeoJSON source.
Symbol layer

A symbol style layer renders icon and text labels at points or along lines on a map. You can use a symbol layer to configure the visual appearance of labels for features in vector tiles.
Symbol layer

To add a symbol layer, you need to first add a vector or GeoJSON source that contains point data. If you want to use icons in this layer, you also need to add images to the style before adding the layer. Then you can use the available properties in symbol layer to customize the appearance of the layer.

map.addLayer({
  id: 'city-label',
  type: 'symbol',
  source: 'labels',
  layout: {
    'text-field': ['get', 'city_name'],
    'text-size': 12
  }
});

EXAMPLE
Symbol layer example

Add labels with variable label placement to a map using a GeoJSON source.
Circle layer

A circle style layer renders one or more filled circles on a map. You can use a circle layer to configure the visual appearance of point or point collection features in vector tiles. A circle layer renders circles whose radii are measured in screen units.
Circle layer

To add a circle layer, you need to first add a vector or GeoJSON source that contains point data. Then you can use the available properties in circle layer to customize the appearance of the layer (for example, radius, color, or offset).

map.addLayer({
  id: 'park-volcanoes',
  type: 'circle',
  source: 'national-park',
  paint: {
    'circle-radius': 6,
    'circle-color': '#B42222'
  }
});

EXAMPLE
Circle layer example

Style circles with a data-driven property.
Fill extrusion layer

A fill-extrusion style layer renders one or more filled (and optionally stroked) extruded (3D) polygons on a map. You can use a fill-extrusion layer to configure the extrusion and visual appearance of polygon or multipolygon features.
Fill extrusion layer

To add a fill-extrusion layer, you need to first add a vector or GeoJSON source that contains polygon data. The data should contain a data property used to determine the height of extrusion of each feature. This may be a physical height in meters or a way to illustrate a non-physical attribute of the area like population in Census blocks. Once you've added an appropriate source, you can use the available properties in fill-extrusion layer class to customize the appearance of the layer (for example, the height, opacity, or color).

map.addLayer({
  id: '3d-buildings',
  source: 'composite',
  'source-layer': 'building',
  filter: ['==', 'extrude', 'true'],
  type: 'fill-extrusion',
  paint: {
    'fill-extrusion-color': '#aaa',
    'fill-extrusion-height': ['get', 'height'],
    'fill-extrusion-base': ['get', 'min_height'],
    'fill-extrusion-opacity': 0.6
  }
});

EXAMPLE
Fill extrusion layer example

Display buildings in 3D using a fill extrusion layer.
Hillshade layer

A hillshade style layer, renders digital elevation model (DEM) data on the client-side.
Hillshade layer

The implementation only supports sources comprised of Mapbox Terrain RGB or Mapzen Terrarium tiles. Once you've added an appropriate source, you can use the available properties in hillshade layer to customize the appearance of the layer.

map.addSource('dem', {
  type: 'raster-dem',
  url: 'mapbox://mapbox.mapbox-terrain-dem-v1'
});
map.addLayer({
  id: 'hillshading',
  source: 'dem',
  type: 'hillshade'
});

EXAMPLE
Hillshade layer example

Add hillshading using Mapbox terrain DEM source.
Heatmap layer

A heatmap style layer renders a range of colors to represent the density of points in an area.
Heatmap layer

To add a heatmap layer, you need to first add a vector or GeoJSON source that contains point data. Then you can use the available properties in heatmap layer to customize the appearance of the layer.

map.addLayer({
  id: 'earthquakes-heat',
  type: 'heatmap',
  source: 'earthquakes',
  paint: {
    'heatmap-color': [
      'interpolate',
      ['linear'],
      ['heatmap-density'],
      0,
      'rgba(33,102,172,0)',
      0.2,
      'rgb(103,169,207)',
      0.4,
      'rgb(209,229,240)',
      0.6,
      'rgb(253,219,199)',
      0.8,
      'rgb(239,138,98)',
      1,
      'rgb(178,24,43)'
    ],
    'heatmap-radius': 20
  }
});

EXAMPLE
Heatmap layer example

Add a heatmap layer using a GeoJSON source with point data.
Raster layer

A raster style layer, renders raster tiles on a map. You can use a raster layer to configure the color parameters of raster tiles.
Raster layer

To add a raster layer, you need to first add a raster source. Then you can use the available properties in raster layer to customize the appearance of the layer.

map.addLayer({
  id: 'radar-layer',
  type: 'raster',
  source: 'radar',
  paint: {
    'raster-fade-duration': 0
  }
});

EXAMPLE
Raster layer example

Add a raster image to a map using an image source and a raster layer.
Background layer

The background style layer, covers the entire map. Use a background style layer to configure a color or pattern to show below all other map content. If the background layer is transparent or omitted from the style, any part of the map view that does not show another style layer is transparent.

You can use the available properties in background layer to customize the appearance of the layer.

map.addLayer({
  type: 'background',
  paint: {
    'background-color': 'blue',
    'background-opacity': 0.3
  }
});



Styling layers with expressions
On this page

    Syntax
    Expression types
    Data-driven styling at runtime
    Zoom-driven styling at runtime
    Light-driven styling in Standard

In Mapbox GL JS, you can specify the value for any layout property, paint property, or filter as an expression. Expressions define how one or more feature property value or the current zoom level are combined using logical, mathematical, string, or color operations to produce the appropriate style property value or filter decision.

A property expression is any expression defined using a reference to feature property data. Property expressions allow the appearance of a feature to change with its properties. They can be used to visually differentiate types of features within the same layer or create data visualizations.

A camera expression is any expression defined using ['zoom']. Such expressions allow the appearance of a layer to change with the map’s zoom level. Zoom expressions can be used to create the illusion of depth and control data density.

There are countless ways to apply property expressions to your application, including:

    Data-driven styling: Specify style rules based on one or more data attribute.
    Arithmetic: Do arithmetic on source data, for example performing calculations to convert units.
    Conditional logic: Use if-then logic, for example to decide exactly what text to display for a label based on which properties are available in the feature or even the length of the name.
    String manipulation: Take control over label text with things like uppercase, lowercase, and title case transforms without having to edit, re-prepare and re-upload your data.

RELATED
Mapbox Style Specification: Expressions

An expression defines a formula for computing the value of the property using the operators described in this section.
Syntax

The Mapbox GL JS expressions follow this format:

["expression_name", argument_0, argument_1]

The expression_name is the expression operator, for example, you would use "*" to multiply two arguments or case to create conditional logic.

The arguments are either literal (numbers, strings, or boolean values) or else themselves expressions. The number of arguments varies based on the expression.

Here's one example using an expression to calculate an arithmetic expression (π * 32):

["*", ["pi"], ["^", 3, 2]]

This example uses the "*" operator to multiply two arguments. The first argument is pi, which is an expression that returns the mathematical constant Pi. The second argument is another expression: a pow expression with two arguments of its own. It will return 32, and the result will be multiplied by π.
Expression types

    Mathematical operators for performing arithmetic and other operations on numeric values
    Logical operators for manipulating boolean values and making conditional decisions
    String operators for manipulating strings
    Data operators for providing access to the properties of source features
    Camera operators for providing access to the parameters defining the current map view

Data-driven styling at runtime

You can use expressions to determine the style of features in a layer based on data properties in the source data. For example, if you have a source containing point data from individual responses to the 2010 U.S. Census and each point has an "ethnicity" data property, you can use expressions to specify the color of each circle based on reported ethnicity.
Data-driven circle layer

The example below uses the match operator to compare the value of the "ethnicity" data property for each point in the source to several possible values. The first argument of the match expression is the value of the "ethnicity" data property. There are several arguments that specify what to do if the value of the data property matches a given string and a final argument that specifies what to do if the value of the data property does not match any of the strings provided.

To read the values of the "ethnicity" data property, this example uses the get operator with "ethnicity" as the sole argument.

Then, it uses stops for the next several arguments for the match expression. Each stop has two arguments: the first is the value to compare to the value of the "ethnicity" data property and the second is the value that should be applied to the layer's circleColor property if the value of the data property matches the first argument.

The second argument of the stop is a color, which is constructed using the rgb operator.

The final argument of the match expression is a fallback value that should be applied to circle-color if the value of the "ethnicity" data property does not match any of the strings provided.

map.addLayer({
  id: 'circle',
  type: 'circle',
  source: 'census',
  paint: {
    // match the value of the data property to a specific color
    'circle-color': [
      'match',
      ['get', 'ethnicity'],
      'White',
      '#fbb03b',
      'Black',
      '#223b53',
      'Hispanic',
      '#e55e5e',
      'Asian',
      '#3bb2d0',
      /* other */ 'black'
    ]
  }
});

EXAMPLE
Data-driven styling example

Style circles with a data-driven property
Zoom-driven styling at runtime

You can use expressions to determine the style of features in a layer based on the camera position, including the zoom level. For example, if you have dense point data displayed using a circle layer, you may want to adjust the radius of circles based on the zoom level to make the data more readable at low zoom levels.

The example below uses the interpolate operator to produce a continuous, smooth series of values between pairs of input and output values ("stops"). Its first argument sets the interpolation type, the second is the value of the zoom level, and the remaining arguments specify the size of the circle radius that should be applied based on the value of the zoom level.

"Exponential" is one of a few types of interpolation available Mapbox expressions. An expression using the exponential operator has one argument: the base, which controls the rate at which the output increases.

The zoom expression does not require any arguments. It will return the value of the current zoom level of the map.

The remaining arguments of the interpolate expression are stops. They represent points along the exponential curve. When a user is viewing the map at zoom level 12 or below, the circles will have a radius of 2. When viewing it at zoom level 22 and above, the circles will have a radius of 180. For all zoom levels between, the radius will be determined by an exponential function and the value will fall somewhere between 2 and 180.

map.addLayer({
  id: 'population',
  type: 'circle',
  source: 'ethnicity-source',
  'source-layer': 'sf2010',
  paint: {
    'circle-radius': [
      // Produce a continuous, smooth series of values
      // between pairs of input and output values
      'interpolate',
      ['exponential', 1.75], // Set the interpolation type
      ['zoom'], // Get current zoom level
      // If the map is at zoom level 12 or below, set circle radius to 2
      12,
      2,
      // If the map is at zoom level 22 or above, set circle radius to 180
      22,
      180
    ]
  }
});

EXAMPLE
Zoom-driven styling example

Change building color based on zoom level
Light-driven styling in Standard

Mapbox Standard uses 3D lighting which affects the entire map, like lighting in the real world. This means that when you switch to dark lights, for example to the “night” preset, your custom layers will also be dark. If you want to change how light affects your custom layer, you will need to configure different variants of the emissive-strength property. These properties control how light is being emitted, for example, background-emissive-strength adjusts the opacity of the background. The different variants of emissive-strength include: background, fill, circle, text, line and many more variants which can be viewed on the layers page of the Mapbox Style Specification.

To learn more about layer types in general, view the layer types style spec documentation.

Here’s an example how you would set *-emissive-strength for a line layer:

map.addLayer({
  id: 'my-line-layer',
  source: 'vector-source',
  'source-layer': 'road',
  paint: {
    'line-emissive-strength': 1
  }
});

This image illustrates how different line-emissive-strength values are impacting the visual appearance of a line layer:
Comparison of different values of emissive strengths


Use Globe in Mapbox GL JS

Most of the latest Mapbox styles use globe by default. Using these styles or a style created them in Studio will enable globe on your map.

Navigation styles default to the Mercator projection.

You can change any other map to globe by setting the projection property.

const map = new mapboxgl.Map({
  container: 'map',
  projection: 'globe'
});

Globe is compatible with all tile sources and map styles (with a few caveats). See examples for custom atmosphere styling and rotating globe.
Atmosphere styling

The latest Mapbox styles include atmosphere by default. You can customize stars and atmosphere with the fog property. To set a custom atmosphere in GL JS:

map.on('style.load', () => {
  map.setFog({
    color: 'rgb(186, 210, 235)', // Lower atmosphere
    'high-color': 'rgb(36, 92, 223)', // Upper atmosphere
    'horizon-blend': 0.02, // Atmosphere thickness (default 0.2 at low zooms)
    'space-color': 'rgb(11, 11, 25)', // Background color
    'star-intensity': 0.6 // Background star brightness (default 0.35 at low zoooms )
  });
});

These properties support zoom expressions, for instance to fade from starry space at low zooms to a blue sky at high zooms.

Atmosphere can also be customized per-style in Mapbox Studio.
Behavior

For any camera zoom level and location, maps in globe will be rendered at roughly the same size. At low zoom levels, the same zoom level will result in features near the poles appearing larger in Mercator, while near the equator features will appear larger in globe. This is a compromise ensuring relatively consistent map appearance given the size distortion inherent in Mercator.
Limitations of Globe

Globe does not yet support CustomLayerInterface.

Globe does not support the deprecated sky layer. We recommend styling the sky and atmosphere with the fog property as described above.

Panning is limited by the poles. In the case where it's important to position the map center at pole, consider a polar projection.


Manage your web map costs
On this page

    Interactive maps
    Non-interactive maps
    Hybrid, interactive and non-interactive maps

This troubleshooting guide shows you different ways to manage your costs for common web map implementations (interactive, non-interactive, and hybrid). The tables in this troubleshooting guide outline common mapping use-cases and offer suggestions for balancing the various cost-effective, performant map options with your ideal end-user experience.

For specific details on how the products discussed in this guide are priced, see the product pricing documentation, linked in each of the following tables.
Note

Every mapping implementation is unique and Mapbox products are optimized for specific use-cases. The way you choose to implement web maps will depend on what end-user experience you want to build. If you're still not sure what is a good option for you after reviewing this documentation, let us know!
Interactive maps

Interactive maps are designed for end-user interaction:
Use case	Example	Recommendations for cost effective use
Interactive large map	A map-based web application in which the map fills the webpage	Use Mapbox GL JS (version 1.0.0 or greater), billed by map load.
Limited interaction large or small map	A travel map of cruise destinations in which all lines are visible on initial map load, meaning users don’t need to pan or interact with the map	Use the Static Tiles API with any tiling client of your choosing. (For example Leaflet, or OpenLayers. Note that these tiling clients are not actively maintained by Mapbox.) In the tiling client, set the max bounds and the min and max zoom levels to limit the number of tiles loaded.
Interactive map below the fold of a webpage	A store locator map anchored at the bottom of a webpage	Use Mapbox GL JS (version 1.0.0 or greater), billed by map load. Consider techniques like lazy loading so that only users who scroll to the map instantiate a map load.
Non-interactive maps

Non-interactive static maps are designed to be passively viewed by end-users:
Use case	Example	Recommendations for cost effective use
Zero-interaction large map	A colorful map used as the backdrop for a website, or a large map image	Use the Static Images API.
Small map in the corner of a page	A small non-interactive map on a real estate page	Use the Static Images API.
Data visualizations using client-side data	Showing different non-interactive styles or layers to different subsets of end-users	Use the Static Images API with style parameters.
Hybrid, interactive and non-interactive maps

Hybrid maps are designed to display a non-interactive preview that leads to an interactive experience:
Use case	Example	Recommendations for cost effective use
No map on load, with a text option to Load Map	A map of store or service locations	Use Mapbox GL JS (version 1.0.0 or greater) behind a Load Map button to delay initialization of the map or with lazy loading.
A static map on load that opens interactive map when clicked	A hiking website that has text descriptions with a Load Map feature that allows end users to interact further with routes	Use the Static Images API for non-interactive the map images (thumbnails). Use Mapbox GL JS (version 1.0.0 or greater), billed by map load, for the interactive map.
Multiple maps on one page	An end-user can see multiple running routes at a glance, and clicking one of the non-interactive map thumbnails opens a larger interactive map	Use the Static Images API for non-interactive the map images (thumbnails). Use Mapbox GL JS (version 1.0.0 or greater), billed by map load, for the interactive map. With Mapbox GL JS version 2.0.0 or greater, each map on the same page is billed individually by map load.

Migrate to Mapbox GL JS v3
On this page

    Update Dependencies
    Explore New Features
        The Mapbox Standard style
        The Mapbox Standard Satellite style
        Layer Slots
        Lighting API
        Style API and expressions improvements
    Migration guide
    Known issues and limitations

Eiffel Tower at Dusk in GL JS v3

Mapbox GL JS v3 enables the Mapbox Standard Style and Mapbox Standard Satellite Style, a new realistic 3D lighting system, 3D models for landmarks, building and terrain shadows and many other visual enhancements, and an ergonomic API for using a new kind of rich, evolving, configurable map styles and seamless integration with custom data.
Update Dependencies

Mapbox GL JS v3 is supported in most modern browsers. Mapbox GL JS v3 is backwards-compatible and existing layers and APIs will continue to work as expected. To use the new Mapbox GL JS v3 in your project, you need to import it using the Mapbox GL JS CDN or install the mapbox-gl npm package.
Mapbox CDN
Module bundler

Include the JavaScript and CSS files in the head of your HTML file.The CSS file is required to display the map and make elements like Popups and Markers work.

<script src='https://api.mapbox.com/mapbox-gl-js/v3.17.0/mapbox-gl.js'></script>
<link href='https://api.mapbox.com/mapbox-gl-js/v3.17.0/mapbox-gl.css' rel='stylesheet' />

Include the following code in the body of your HTML file.

<div id='map' style='width: 400px; height: 300px;'></div>
<script>
mapboxgl.accessToken = 'pk.eyJ1IjoidHdpdG9jb2RlIiwiYSI6ImNtazkzZWY1ODFtZnIzZnB0bHlhZ2Eyem8ifQ.wvcTVGvt0pFMu7EjRF_73w';
const map = new mapboxgl.Map({
	container: 'map', // container ID
	center: [-74.5, 40], // starting position [lng, lat]
	zoom: 9, // starting zoom
});
</script>

To use Mapbox GL JS, you need to have a Mapbox access token. This access token associates your map with a Mapbox account. For more information on creating and using access tokens, see our token management documentation.
Explore New Features
The Mapbox Standard style

We're excited to announce the launch of Mapbox Standard, our latest Mapbox style, now accessible to all customers. The new Mapbox Standard core style enables a highly performant and elegant 3D mapping experience with powerful dynamic lighting capabilities, landmark 3D buildings, and an expertly crafted symbolic aesthetic.
London at Day in GL JS v3

With Mapbox Standard, we are also introducing a new paradigm for how to interact with map styles. When you use this style in your application we will continuously update your basemap with the latest features with no additional work required from you. This ensures that your users will always have the latest features of our maps. You can get more information about the available presets and configuration options of the Standard style in the style documentation.

    The Mapbox Standard Style (mapbox://styles/mapbox/standard) is now enabled by default when no style option is provided to the Map constructor. Or, you can still explicitly set the style by passing the URL to the style option of the Map constructor.

    The Mapbox Standard Style offers a dynamic way to personalize your maps. The map's appearance can be changed using the map.setConfigProperty method, where you reference the Standard Style as basemap, followed by the configuration property, like light preset or label visibility, and then specify the desired value.

    The Mapbox Standard style features 4 light presets: "Day", "Dusk", "Dawn", and "Night". After the style has loaded, the light preset can be changed from the default, "Day", to another preset with a single line of code:

map.on('style.load', () => {
  map.setConfigProperty('basemap', 'lightPreset', 'dusk');
});

Changing the light preset will alter the colors and shadows on your map to reflect the time of day. For more information, refer to the Lighting API section.

Similarly, you can set other configuration properties on the Standard style such as showing POIs, place labels, or specific fonts:

map.on('style.load', () => {
  map.setConfigProperty('basemap', 'showPointOfInterestLabels', false);
});

The Standard style offers 8 configuration properties for developers to change when they import it into their own style:
Property	Type	Description
showPlaceLabels	Bool	Shows and hides place label layers.
showRoadLabels	Bool	Shows and hides all road labels, including road shields.
showPointOfInterestLabels	Bool	Shows or hides all POI icons and text.
showTransitLabels	Bool	Shows or hides all transit icons and text.
show3dObjects	Bool	Shows or hides all 3D layers (3D buildings, landmarks, trees, etc.) including shadows, ambient occlusion, and flood lights.
theme	String	Switches between 3 themes: default, faded and monochrome.
lightPreset	String	Switches between 4 time-of-day states: dusk, dawn, day, and night.
font	String	Defines font family for the style from predefined options.
The Mapbox Standard Satellite style

The Standard Satellite Style (mapbox://styles/mapbox/standard-satellite) combines updated satellite imagery and vector layers to offer users improved clarity and detail. Like Standard style, the Satellite Style receives all updates automatically and also supports light presets. Additionally, it introduces two new configurations showRoadsAndTransit and showPedestrianRoads. Users can now choose to hide roads, simplifying the map style for a better focus on specific areas or features.

The Standard Satellite style offers 8 configuration properties for developers to change when they import it into their own style:
Property	Type	Description
showRoadsAndTransit	Bool	Shows and hides all roads and transit networks.
showPedestrianRoads	Bool	Shows and hides all pedestrian roads, paths, trails.
showPlaceLabels	Bool	Shows and hides place label layers.
showRoadLabels	Bool	Shows and hides all road labels, including road shields.
showPointOfInterestLabels	Bool	Shows or hides all POI icons and text.
showTransitLabels	Bool	Shows or hides all transit icons and text.
lightPreset	String	Switches between 4 time-of-day states: dusk, dawn, day, and night.
font	String	Defines font family for the style from predefined options.
Important: Standard satellite style doesn't support theme and show3dObjects configuration.		
Layer Slots

Mapbox Standard and Mapbox Standard Satellite are making adding your own data layers easier for you through the concept of slots. Slots are predetermined locations in the style where your layer will be added to (such as on top of existing land layers, but below all labels). To do this, we've added a new slot property to each Layer. This property allows you to identify which slot in the Mapbox Standard your new layer should be placed in. To add custom layers in the appropriate location in the Standard or Standard Satellite styles layer stack, we added 3 carefully designed slots that you can leverage to place your layer:
Slot	Description
bottom	Above polygons (land, landuse, water, etc.)
middle	Above lines (roads, etc.) and behind 3D buildings
top	Above POI labels and behind Place and Transit labels
not specified	If there is no identifier, the new layer will be placed above all existing layers in the style
Slots and performance-optimized layers reordering

During 3D globe and terrain rendering, GL JS aims to batch multiple layers together for optimal performance. This process might lead to a rearrangement of layers. Layers draped over globe and terrain, such as fill, line, background, hillshade, and raster, are rendered first. These layers are rendered underneath symbols, regardless of whether they are placed in the middle or top slots or without a designated slot.

Set the preferred slot on the Layer object before adding it to your map and your layer will be appropriately placed in the Standard style's layer stack.

map.addLayer({
  id: 'points-of-interest',
  slot: 'middle',
  source: {
    type: 'vector',
    url: 'mapbox://mapbox.mapbox-streets-v8'
  },
  'source-layer': 'poi_label',
  type: 'circle'
});

Important: For the new Standard and Standard Satellite style, you can only add layers to these three slots (bottom, middle, top) within the Standard and Standard Satellite style basemaps.

Like with the classic Mapbox styles, you can still use the layer position in map.addLayer(layer, beforeId) method when importing the Standard Style or Standard Satellite style. But, this method is only applicable to custom layers you have added yourself. If you add two layers to the same slot with a specified layer position the latter will define order of the layers in that slot.

When using the Standard style or Standard Satellite style, you get the latest basemap rendering features, map styling trends and data layers as soon as they are available, without requiring any manual migration/integration. On top of this, you'll still have the ability to introduce your own data to the map and control your user's experience. If you have feedback or questions about the Mapbox Standard style or Standard Satellite style reach out to: hey-map-design@mapbox.com.

Classic Mapbox styles (such as Mapbox Streets, Mapbox Light, and Mapbox Satellite Streets) and any custom styles you have built in Mapbox Studio will still work like they do in v2, so no changes are required.
Lighting API

The new Standard and Standard Satellite style and its dynamic lighting is powered by the new Style and Lighting APIs that you can experiment with. The following experimental APIs can be used to control the look and feel of the map.

In GL JS v3 we've introduced new experimental lighting APIs to give you control of lighting and shadows in your map when using 3D objects: AmbientLight and DirectionalLight. We've also added new APIs on FillExtrusionLayer and LineLayer to support this 3D lighting styling and enhance your ability to work with 3D model layers. Together, these properties can illuminate your 3D objects such as buildings and terrain to provide a more realistic and immersive map experience for your users. Set these properties at runtime to follow the time of day, a particular mood, or other lighting goals in your map.
New York City at Night in GL JS v3
Style API and expressions improvements

We have introduced a new set of expressions to enhance your styling capabilities:

    Introduced hsl, hsla color expression: These expressions allow you to define colors using hue, saturation, lightness format.
    Introduced random expression: Generate random values using this expression. Use this expression to generate random values, which can be particularly helpful for introducing randomness into your map data.
    Introduced measureLight expression lights configuration property: Create dynamic styles based on lighting conditions.
    Introduced config expression: Retrieves the configuration value for the given option.
    Introduced raster-value expression: Returns the raster value of a pixel computed via raster-color-mix.
    Introduced distance expression: Returns the shortest distance in meters between the evaluated feature and the input geometry.

Mapbox GL JS v3 also introduces a new set of paint properties:

    background:
        background-emissive-strength
    circle:
        circle-emissive-strength
    fill:
        fill-emissive-strength
        fill-extrusion-ambient-occlusion-ground-attenuation
        fill-extrusion-ambient-occlusion-ground-radius
        fill-extrusion-ambient-occlusion-wall-radius
        fill-extrusion-flood-light-color
        fill-extrusion-flood-light-ground-attenuation
        fill-extrusion-flood-light-ground-radius
        fill-extrusion-flood-light-intensity
        fill-extrusion-flood-light-wall-radius
        fill-extrusion-vertical-scale
    icon:
        icon-emissive-strength
        icon-image-cross-fade
    line:
        line-emissive-strength
    raster:
        raster-color-mix
        raster-color-range
        raster-color
    text:
        text-emissive-strength

Migration guide

Mapbox GL JS v3 is backwards-compatible and existing layers and APIs will continue to work as expected, but there are some things to be aware of before upgrading from old versions.

    Mapbox GL JS is distributed as an ES6 compatible JavaScript bundle compatible with all major modern browsers. If you transpile Mapbox GL JS, upgrading from v1 to v3 may require modifications to your bundler configuration. See Transpiling for detailed guidance.
    Mapbox GL JS has not supported Internet Explorer 11 since v1. If you need to support Internet Explorer, consider using the Mapbox Static Images API for non-interactive maps or using the Mapbox Static Tiles API with another library for interactive maps.
    The default maxPitch increased from 60° to 85° in v2. This change makes it possible to view above the horizon when the map is fully pitched. We recommend adding a customizable sky with atmospheric styling. If the map's fog property is not set, the area above the horizon will be transparent to any pixels behind the map.
    A valid Mapbox access token is required to instantiate a Map object. Assign a token using mapboxgl.accessToken or in the Map constructor options. To create an account or a new access token, visit https://account.mapbox.com.
    The action that triggers a map load has changed. In v1, a map load would occur whenever a Map instance was created and the map requested Mapbox-hosted tile resources. In v3, a map load occurs whenever a Map instance is created regardless of whether the map requests any Mapbox-hosted tile resources. Before updating an existing implementation of GL JS to v3, review the pricing documentation.
    From v3.5.0, Mapbox GL JS uses Typescript instead of Flow. Community types @types/mapbox-gl are not fully compatible with the new first-class types. Users relying on the community types may experience breaking changes. Remove the @types/mapbox-gl dependency and refer to the v3.5.0 migration guide for instructions on upgrading, resolving common issues, and asking questions about the migration to the first-class types.
    From v3.11.0, the at expression does not interpolate anymore. Use at-interpolated if you want to keep the old behavior.

Known issues and limitations

To report new issues with Mapbox GL JS v3, create a bug report on GitHub.

    Discontinued WebGL 1 support. WebGL 2 is now mandatory for GL JS v3 usage, aligned with universal browser support.
    During 3D globe and terrain rendering, GL JS aims to batch multiple layers together for optimal performance. This process might lead to a rearrangement of layers. Layers draped over globe and terrain, such as fill, line, background, hillshade, and raster, are rendered first. These layers are rendered underneath symbols, regardless of whether they are placed in the middle or top slots when using Mapbox Standard Style or without a designated slot.
    In Safari 17 private browsing mode, Apple's Advanced Privacy Protection introduces noise into key fingerprinting areas like 2D Canvas and WebGL and may cause unexpected terrain spikes in GL JS v3.
    When using the globe projection, markers that are on the non-visible side of the globe have incorrect initial positions.
    Triggering a resize event while a flyTo animation is in progress changes the final animation position.
    Markers and the screen area receptive to clicks diverge between zoom level 5 and 6 under some circumstances when using the globe projection.


Gestures and Events
On this page

    Default Map Gestures
        Desktop Gestures
        Mobile Gestures
    Enable and Disable Default Gestures
    User Interaction Events
    External Interactions
        Zoom Control
        Fly the Camera
        Show or Hide a Layer

This guide explains how to work with user gestures and events in Mapbox GL JS. You'll learn about default map gestures, how to enable and disable gestures, how to listen for user interactions on the map and how to control the map from external events.
Default Map Gestures

Mapbox GL JS provides intuitive gestures to interact with the map. Gestures vary between desktop and mobile devices.
Desktop Gestures

    Pan around: Click and drag with mouse.
    Adjust pitch: Right-click + drag up/down.
    Gradually zoom: Scroll mouse wheel or use touch pinch gesture.
    Rotate: Right-click + drag left/right. (Hold control + click + drag left/right on Mac)
    Zoom in one level: Double-click.
    Zoom out one level: Hold Shift and double-click.
    Quick zoom: Hold Shift + drag a box.

Mobile Gestures

    Pan around: Tap and drag with touch screen.
    Adjust pitch: Two-finger drag up/down.
    Gradually zoom: Touch pinch gesture.
    Rotate: Two-finger rotate.
    Zoom in one level: Double-tap.
    Zoom out one level: Two-finger tap.

Enable and Disable Default Gestures

You can enable or disable specific gestures when instantiating a map using the dragPan, scrollZoom, boxZoom, dragRotate, keyboard, and touchZoomRotate options.

Example:

const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [0, 0],
    zoom: 2,
    dragPan: true, // Enable or disable drag panning
    scrollZoom: false, // Disable scroll zoom
    boxZoom: true, // Enable box zoom
    dragRotate: true, // Enable drag rotation
    keyboard: true, // Enable keyboard controls
    touchZoomRotate: true // Enable touch zoom & rotation
});

You can also enable and disable interactions after the map has been created:

map.scrollZoom.disable();  // Disable scroll zoom
map.scrollZoom.enable();   // Enable scroll zoom

EXAMPLE
Disable map rotation

See an example of a map with rotation disabled.
EXAMPLE
Disable scroll zoom

See an example of a map with scroll zoom disabled.
EXAMPLE
Display a non-interactive map

See an example of a map with all default gestures disabled.
User Interaction Events

You can listen for user interactions on the map object by using events. Some common event types include:
Event Name	Description
move	Fires continuously as the map is panned or zoomed
moveend	Fires when a panning movement has completed
zoom	Fires continuously while the map is zooming
zoomend	Fires when zooming has completed
rotate	Fires continuously while the map is rotating
rotateend	Fires when rotation has completed
pitch	Fires continuously when the pitch is changing
click	Fires when the user clicks the map

These listeners are used with the on method:

map.on('move', () => {
    console.log('Map is moving');
});

map.on('click', (e) => {
    console.log(`Clicked at: ${e.lngLat.lng}, ${e.lngLat.lat}`);
});

They can also be used with the Interactions API to handle interactions on layers, featuresets, or the map itself.

map.addInteraction('my-polygon-click-interaction', {
  type: 'click',
  target: { layerId: 'polygons' },
  handler: (e) => {
    map.setFeatureState(e.feature, {highlight: true});
  }
});

map.addInteraction('building-mouseenter', {
  type: 'mouseenter',
  target: {featuresetId: 'buildings', importId: 'basemap'},
  handler: (e) => {
    map.setFeatureState(e.feature, {highlight: true});
  }
});

Explore all available events in the API reference documentation.
EXAMPLE
Add feature-level interactions to a map

See an example of a map with interactions on a specific layer.
EXAMPLE
Add interactions to a Mapbox Standard Style

See an example of a map with interactions on a featureset of the Mapbox Standard Style.
External Interactions

You can also control the map using external UI elements like buttons or sliders. Use the map object's methods to programmatically control the map.
Zoom Control

You can build your own zoom in/out UI and use the zoomIn and zoomOut methods to control the map.


const zoomInButton = document.getElementById('zoom-in');

zoomInButton.addEventListener('click', () => {
    map.zoomIn();
});

Fly the Camera

Use the flyTo method to smoothly transition the map to a new location when the user clicks a reset button.

 const zoomOutButton = document.getElementById('reset-map-view');
zoomOutButton.addEventListener('click', () => {
    map.flyTo({
        center: [0, 0],
        zoom: 2
    });
});

EXAMPLE
Fly to a location

See an example of a map with a button that triggers a fly-to animation.
Show or Hide a Layer

Show or hide a layer in the map's style when the user clicks a checkbox.


const checkbox = document.getElementById('toggle-layer');
checkbox.addEventListener('change', (event) => {
    const layerId = 'my-layer';
    if (event.target.checked) {
        map.setLayoutProperty(layerId, 'visibility', 'visible');
    } else {
        map.setLayoutProperty(layerId, 'visibility', 'none');
    }
});


Interactions API
On this page

    Adding an interaction to a map layer
    Adding an interaction to a featureset
    Setting feature states
    Adding an interaction to the map

The new Interactions API is a toolset that allows you to handle interactions on layers, predefined featuresets in evolving basemap styles like Standard, and the map itself. The API is available starting from Mapbox GL JS v3.9.0.

To use the API, you define interaction handlers for events like 'click' or 'mouseenter' that target specific map layers, featuresets, or the map itself. When a user interacts with map features belonging to one of these sets, the API will call the appropriate interaction handler for that feature that was interacted with.
Adding an interaction to a map layer

Add interactions to the map by indicating an event type ('click', 'mouseenter', 'mouseleave', etc), a target (either a layer or featureset), and a handler function.

Use the addInteraction method to add the interaction:

map.addInteraction('my-polygon-click-interaction', {
  type: 'click',
  target: { layerId: polygons },
  handler: (e) => {
    map.setFeatureState(e.feature, {highlight: true});
  }
});

The handler in the example above will be called each time a user clicks a feature rendered on the polygons layer. The handler receives an event object with information about the interaction, including the feature that was interacted with. In this example, the handler sets a feature state on the clicked feature to highlight it.

You can add an interaction at any time, there is no need to wait for the style to load. If there is no layer with the name provided, then no interaction will be added.

Interactions can be removed by calling the removeInteraction method:

map.removeInteraction('my-polygon-click-interaction');

EXAMPLE
Layer Interaction

See a working example of using addInteraction to add hover and click interactions to a map layer.
Adding an interaction to a featureset

Interactions can also be added to a featureset. Featuresets are named groups of layers that can be defined in an evolving basemap style. In the Mapbox Standard Style, there are predefined Points-of-Interest (POI), Place Labels, and Buildings featuresets that include all corresponding features in the map. You can add interactions to your map that target these featuresets.

To see the available featuresets in the Standard Style, see the Mapbox Standard Style API reference documentation.

map.addInteraction('poi-click', {
  type: 'click',
  target: {featuresetId: 'poi', importId: 'basemap'},
  handler(e) {
    console.log(e.feature);
  }
});

When you use a featureset, the interaction handler will receive a Feature object that contains the feature's properties and geometry. You can use this information to customize the behavior of your application based on the specific feature that was interacted with.
EXAMPLE
Featureset Interaction

See a working example of using addInteraction to interact with featuresets in the Mapbox Standard style.
Setting feature states

After a feature is returned from the interaction, you can set its feature state. Setting the feature state allows you to control the appearance of individual features within a featureset.

For example, you may want to highlight individual buildings after a user hovers the mouse over them. To do this, you would add an interaction targeting the buildings featureset. When a user taps on a building in this featureset, the building feature is available in the handler function. You then set the feature state for this feature's highlight configuration option to true. By default, highlighted buildings in Mapbox Standard will be displayed in blue, as shown in the image below. You can customize the color of selected buildings.

map.addInteraction('building-mouseenter', {
  type: 'mouseenter',
  target: {featuresetId: 'buildings', importId: 'basemap'},
  handler: (e) => {
    map.setFeatureState(e.feature, {highlight: true});
  }
});

Each predefined featureset in the Standard Style has appropriate configuration options that can be modified at runtime in this way. Explore the Mapbox Standard Documentation to learn more about the specific configuration options available for each featureset.
EXAMPLE
Featureset Interaction

See a working example of using addInteraction to update feature states on featuresets in the Mapbox Standard style.
Adding an interaction to the map

You can use addInteraction in a way that doesn't take any layer or featureset by omitting the target option. This lets you handle events on the map itself. For example, you can add an interaction that listens for 'click' events anywhere on the map and logs the coordinates of the click to the console:

map.addInteraction('map-click', {
  type: 'click',
  handler: (e) => {
    console.log(`Clicked at: ${e.lngLat.lng}, ${e.lngLat.lat}`);
  }
});

Skip to main content
Docs

English

Mapbox GL JS

    Guides

API Reference

        Map
        Properties and options
        Markers and controls
        User interaction handlers
        Sources
        Events and event types
        Geography and geometry
    Plugins and frameworks
    Examples
    Style Specificationshare
    Tutorialsshare
    Troubleshootingshare

    All docschevron-rightMapbox GL JSchevron-rightAPI Referencechevron-rightMap

Map
Search GL JS API Reference
On this page

    Parameters
    Example
    Instance members
        Interaction handlers
        Controls
        Map constraints
        Point conversion
        Movement state
        Working with events
        Querying features
        Working with styles
        Sources
        Images
        Models
        Layers
        Style properties
        Feature state
        Lifecycle
        Debug features
    Events
    Related

githubsrc/ui/map.ts

The Map object represents the map on your page. It exposes methods and properties that enable you to programmatically change the map, and fires events as users interact with it.

You create a Map by specifying a container and other options. Then Mapbox GL JS initializes the map on the page and returns your Map object.
Extends Evented.
new Map class(options: Object)
Parameters
Name	Description
options
Object
	
options.accessToken
string
(default null)
	If specified, map will use this token instead of the one defined in mapboxgl.accessToken .
options.antialias
boolean
(default false)
	If true , the gl context will be created with MSAA antialiasing . This is false by default as a performance optimization.
options.attributionControl
boolean
(default true)
	If true , an AttributionControl will be added to the map.
options.bearing
number
(default 0)
	The initial bearing (rotation) of the map, measured in degrees counter-clockwise from north. If bearing is not specified in the constructor options, Mapbox GL JS will look for it in the map's style object. If it is not specified in the style, either, it will default to 0 .
options.bearingSnap
number
(default 7)
	The threshold, measured in degrees, that determines when the map's bearing will snap to north. For example, with a bearingSnap of 7, if the user rotates the map within 7 degrees of north, the map will automatically snap to exact north.
options.bounds
LngLatBoundsLike
(default null)
	The initial bounds of the map. If bounds is specified, it overrides center and zoom constructor options.
options.boxZoom
boolean
(default true)
	If true , the "box zoom" interaction is enabled (see BoxZoomHandler ).
options.center
LngLatLike
(default [0,0])
	The initial geographical centerpoint of the map. If center is not specified in the constructor options, Mapbox GL JS will look for it in the map's style object. If it is not specified in the style, either, it will default to [0, 0] Note: Mapbox GL uses longitude, latitude coordinate order (as opposed to latitude, longitude) to match GeoJSON.
options.clickTolerance
number
(default 3)
	The max number of pixels a user can shift the mouse pointer during a click for it to be considered a valid click (as opposed to a mouse drag).
options.collectResourceTiming
boolean
(default false)
	If true , Resource Timing API information will be collected for requests made by GeoJSON and Vector Tile web workers (this information is normally inaccessible from the main Javascript thread). Information will be returned in a resourceTiming property of relevant data events.
options.config
Object
(default null)
	The initial configuration options for the style fragments. Each key in the object is a fragment ID (e.g., basemap ) and each value is a configuration object.
options.container
(HTMLElement | string)
	The HTML element in which Mapbox GL JS will render the map, or the element's string id . The specified element must have no children.
options.cooperativeGestures
boolean?
	If true , scroll zoom will require pressing the ctrl or ⌘ key while scrolling to zoom map, and touch pan will require using two fingers while panning to move the map. Touch pitch will require three fingers to activate if enabled.
options.crossSourceCollisions
boolean
(default true)
	If true , symbols from multiple sources can collide with each other during collision detection. If false , collision detection is run separately for the symbols in each source.
options.customAttribution
(string | Array<string>)
(default null)
	String or strings to show in an AttributionControl . Only applicable if options.attributionControl is true .
options.doubleClickZoom
boolean
(default true)
	If true , the "double click to zoom" interaction is enabled (see DoubleClickZoomHandler ).
options.dragPan
(boolean | Object)
(default true)
	If true , the "drag to pan" interaction is enabled. An Object value is passed as options to DragPanHandler#enable .
options.dragRotate
boolean
(default true)
	If true , the "drag to rotate" interaction is enabled (see DragRotateHandler ).
options.fadeDuration
number
(default 300)
	Controls the duration of the fade-in/fade-out animation for label collisions, in milliseconds. This setting affects all symbol layers. This setting does not affect the duration of runtime styling transitions or raster tile cross-fading.
options.failIfMajorPerformanceCaveat
boolean
(default false)
	If true , map creation will fail if the performance of Mapbox GL JS would be dramatically worse than expected (a software renderer would be used).
options.fitBoundsOptions
Object
(default null)
	A Map#fitBounds options object to use only when fitting the initial bounds provided above.
options.hash
(boolean | string)
(default false)
	If true , the map's position (zoom, center latitude, center longitude, bearing, and pitch) will be synced with the hash fragment of the page's URL. For example, http://path/to/my/page.html#2.59/39.26/53.07/-24.1/60 . An additional string may optionally be provided to indicate a parameter-styled hash, for example http://path/to/my/page.html#map=2.59/39.26/53.07/-24.1/60&foo=bar , where foo is a custom parameter and bar is an arbitrary hash distinct from the map hash.
options.interactive
boolean
(default true)
	If false , no mouse, touch, or keyboard listeners will be attached to the map, so it will not respond to interaction.
options.keyboard
boolean
(default true)
	If true , keyboard shortcuts are enabled (see KeyboardHandler ).
options.language
("auto" | string | Array<string>)
(default null)
	A string with a BCP 47 language tag, or an array of such strings representing the desired languages used for the map's labels and UI components. Languages can only be set on Mapbox vector tile sources. By default, GL JS will not set a language so that the language of Mapbox tiles will be determined by the vector tile source's TileJSON. Valid language strings must be a BCP-47 language code . Unsupported BCP-47 codes will not include any translations. Invalid codes will result in an recoverable error. If a label has no translation for the selected language, it will display in the label's local language. If option is set to auto , GL JS will select a user's preferred language as determined by the browser's window.navigator.language property. If the locale property is not set separately, this language will also be used to localize the UI for supported languages.
options.locale
Object
(default null)
	A patch to apply to the default localization table for UI strings such as control tooltips. The locale object maps namespaced UI string IDs to translated strings in the target language; see src/ui/default_locale.js for an example with all supported string IDs. The object may specify all UI strings (thereby adding support for a new translation) or only a subset of strings (thereby patching the default translation table).
options.localFontFamily
string
(default null)
	Defines a CSS font-family for locally overriding generation of all glyphs. Font settings from the map's style will be ignored, except for font-weight keywords (light/regular/medium/bold). If set, this option overrides the setting in localIdeographFontFamily.
options.localIdeographFontFamily
string
(default 'sans-serif')
	Defines a CSS font-family for locally overriding generation of glyphs in the 'CJK Unified Ideographs', 'Hiragana', 'Katakana', 'Hangul Syllables' and 'CJK Symbols and Punctuation' ranges. In these ranges, font settings from the map's style will be ignored, except for font-weight keywords (light/regular/medium/bold). Set to false , to enable font settings from the map's style for these glyph ranges. Note that Mapbox Studio sets this value to false by default. The purpose of this option is to avoid bandwidth-intensive glyph server requests. For an example of this option in use, see Use locally generated ideographs .
options.logoPosition
string
(default 'bottom-left')
	A string representing the position of the Mapbox wordmark on the map. Valid options are top-left , top-right , bottom-left , bottom-right .
options.maxBounds
LngLatBoundsLike
(default null)
	If set, the map will be constrained to the given bounds.
options.maxPitch
number
(default 85)
	The maximum pitch of the map (0-85).
options.maxTileCacheSize
number
(default null)
	The maximum number of tiles stored in the tile cache for a given source. If omitted, the cache will be dynamically sized based on the current viewport.
options.maxZoom
number
(default 22)
	The maximum zoom level of the map (0-24).
options.minPitch
number
(default 0)
	The minimum pitch of the map (0-85).
options.minTileCacheSize
number
(default null)
	The minimum number of tiles stored in the tile cache for a given source. Larger viewports use more tiles and need larger caches. Larger viewports are more likely to be found on devices with more memory and on pages where the map is more important. If omitted, the cache will be dynamically sized based on the current viewport.
options.minZoom
number
(default 0)
	The minimum zoom level of the map (0-24).
options.performanceMetricsCollection
boolean
(default true)
	If true , mapbox-gl will collect and send performance metrics.
options.pitch
number
(default 0)
	The initial pitch (tilt) of the map, measured in degrees away from the plane of the screen (0-85). If pitch is not specified in the constructor options, Mapbox GL JS will look for it in the map's style object. If it is not specified in the style, either, it will default to 0 .
options.pitchRotateKey
("Control" | "Alt" | "Shift" | "Meta")
(default 'Control')
	Allows overriding the keyboard modifier key used for pitch/rotate interactions from Control to another modifier key.
options.pitchWithRotate
boolean
(default true)
	If false , the map's pitch (tilt) control with "drag to rotate" interaction will be disabled.
options.preserveDrawingBuffer
boolean
(default false)
	If true , the map's canvas can be exported to a PNG using map.getCanvas().toDataURL() . This is false by default as a performance optimization.
options.projection
ProjectionSpecification
(default 'mercator')
	The projection the map should be rendered in. Supported projections are:

    Albers equal-area conic projection as albers
    Equal Earth equal-area pseudocylindrical projection as equalEarth
    Equirectangular (Plate Carrée/WGS84) as equirectangular
    3d Globe as globe
    Lambert Conformal Conic as lambertConformalConic
    Mercator cylindrical map projection as mercator
    Natural Earth pseudocylindrical map projection as naturalEarth
    Winkel Tripel azimuthal map projection as winkelTripel Conic projections such as Albers and Lambert have configurable center and parallels properties that allow developers to define the region in which the projection has minimal distortion; see the example for how to configure these properties.

options.refreshExpiredTiles
boolean
(default true)
	If false , the map won't attempt to re-request tiles once they expire per their HTTP cacheControl / expires headers.
options.renderWorldCopies
boolean
(default true)
	If true , multiple copies of the world will be rendered side by side beyond -180 and 180 degrees longitude. If set to false :

    When the map is zoomed out far enough that a single representation of the world does not fill the map's entire container, there will be blank space beyond 180 and -180 degrees longitude.
    Features that cross 180 and -180 degrees longitude will be cut in two (with one portion on the right edge of the map and the other on the left edge of the map) at every zoom level.

options.respectPrefersReducedMotion
boolean
(default true)
	If set to true , the map will respect the user's prefers-reduced-motion browser setting and apply a reduced motion mode, minimizing animations and transitions. When set to false , the map will always ignore the prefers-reduced-motion settings, regardless of the user's preference, making all animations essential.
options.scrollZoom
(boolean | Object)
(default true)
	If true , the "scroll to zoom" interaction is enabled. An Object value is passed as options to ScrollZoomHandler#enable .
options.spriteFormat
("raster" | "icon_set" | "auto")
(default 'auto')
	The format of the image sprite to use. If set to 'auto' , vector iconset will be used for all mapbox-hosted sprites and raster sprite for all custom URLs.
options.style
(Object | string)
(default 'mapbox://styles/mapbox/standard')
	The map's Mapbox style. This must be an a JSON object conforming to the schema described in the Mapbox Style Specification , or a URL to such JSON. Can accept a null value to allow adding a style manually.

To load a style from the Mapbox API, you can use a URL of the form mapbox://styles/:owner/:style, where :owner is your Mapbox account name and :style is the style ID. You can also use a Mapbox-owned style:

    mapbox://styles/mapbox/standard
    mapbox://styles/mapbox/streets-v12
    mapbox://styles/mapbox/outdoors-v12
    mapbox://styles/mapbox/light-v11
    mapbox://styles/mapbox/dark-v11
    mapbox://styles/mapbox/satellite-v9
    mapbox://styles/mapbox/satellite-streets-v12
    mapbox://styles/mapbox/navigation-day-v1
    mapbox://styles/mapbox/navigation-night-v1.

Tilesets hosted with Mapbox can be style-optimized if you append ?optimize=true to the end of your style URL, like mapbox://styles/mapbox/streets-v11?optimize=true. Learn more about style-optimized vector tiles in our API documentation.
options.testMode
boolean
(default false)
	Silences errors and warnings generated due to an invalid accessToken, useful when using the library to write unit tests.
options.touchPitch
(boolean | Object)
(default true)
	If true , the "drag to pitch" interaction is enabled. An Object value is passed as options to TouchPitchHandler .
options.touchZoomRotate
(boolean | Object)
(default true)
	If true , the "pinch to rotate and zoom" interaction is enabled. An Object value is passed as options to TouchZoomRotateHandler#enable .
options.trackResize
boolean
(default true)
	If true , the map will automatically resize when the browser window resizes.
options.transformRequest
RequestTransformFunction
(default null)
	A callback run before the Map makes a request for an external URL. The callback can be used to modify the url, set headers, or set the credentials property for cross-origin requests. Expected to return a RequestParameters object with a url property and optionally headers and credentials properties.
options.worldview
string
(default null)
	Sets the map's worldview. A worldview determines the way that certain disputed boundaries are rendered. By default, GL JS will not set a worldview so that the worldview of Mapbox tiles will be determined by the vector tile source's TileJSON. Valid worldview strings must be an ISO alpha-2 country code . Unsupported ISO alpha-2 codes will fall back to the TileJSON's default worldview. Invalid codes will result in a recoverable error.
options.zoom
number
(default 0)
	The initial zoom level of the map. If zoom is not specified in the constructor options, Mapbox GL JS will look for it in the map's style object. If it is not specified in the style, either, it will default to 0 .
Example

const map = new mapboxgl.Map({
    container: 'map',
    center: [-122.420679, 37.772537],
    zoom: 13,
    style: 'mapbox://styles/mapbox/standard',
    config: {
        // Initial configuration for the Mapbox Standard style set above. By default, its ID is `basemap`.
        basemap: {
            // Here, we're setting the light preset to `night`.
            lightPreset: 'night'
        }
    }
});

const map = new mapboxgl.Map({
    container: 'map', // container ID
    center: [-122.420679, 37.772537], // starting position [lng, lat]
    zoom: 13, // starting zoom
    style: 'mapbox://styles/mapbox/streets-v11', // style URL or style object
    hash: true, // sync `center`, `zoom`, `pitch`, and `bearing` with URL
    // Use `transformRequest` to modify requests that begin with `http://myHost`.
    transformRequest: (url, resourceType) => {
        if (resourceType === 'Source' && url.startsWith('http://myHost')) {
            return {
                url: url.replace('http', 'https'),
                headers: {'my-custom-header': true},
                credentials: 'include'  // Include cookies for cross-origin requests
            };
        }
    }
});

Instance Members
Search Instance Members
Interaction handlers

The map's ScrollZoomHandler, which implements zooming in and out with a scroll wheel or trackpad. Find more details and examples using scrollZoom in the ScrollZoomHandler section.
Type
ScrollZoomHandler

The map's BoxZoomHandler, which implements zooming using a drag gesture with the Shift key pressed. Find more details and examples using boxZoom in the BoxZoomHandler section.
Type
BoxZoomHandler

The map's DragRotateHandler, which implements rotating the map while dragging with the right mouse button or with the Control key pressed. Find more details and examples using dragRotate in the DragRotateHandler section.
Type
DragRotateHandler

The map's DragPanHandler, which implements dragging the map with a mouse or touch gesture. Find more details and examples using dragPan in the DragPanHandler section.
Type
DragPanHandler

The map's KeyboardHandler, which allows the user to zoom, rotate, and pan the map using keyboard shortcuts. Find more details and examples using keyboard in the KeyboardHandler section.
Type
KeyboardHandler

The map's DoubleClickZoomHandler, which allows the user to zoom by double clicking. Find more details and examples using doubleClickZoom in the DoubleClickZoomHandler section.
Type
DoubleClickZoomHandler

The map's TouchZoomRotateHandler, which allows the user to zoom or rotate the map with touch gestures. Find more details and examples using touchZoomRotate in the TouchZoomRotateHandler section.
Type
TouchZoomRotateHandler

The map's TouchPitchHandler, which allows the user to pitch the map with touch gestures. Find more details and examples using touchPitch in the TouchPitchHandler section.
Type
TouchPitchHandler
Controls

Adds an IControl to the map, calling control.onAdd(this).
Parameters
Name	Description
control
IControl
	The IControl to add.
position
string?
	Position on the map to which the control will be added. Valid values are 'top-left' , 'top' , 'top-right' , 'right' , 'bottom-right' , 'bottom' , 'bottom-left' , and 'left' . Defaults to 'top-right' .
Returns
Map: Returns itself to allow for method chaining.
Example

// Add zoom and rotation controls to the map.
map.addControl(new mapboxgl.NavigationControl());

Related

    Example: Display map navigation controls 

Removes the control from the map.
Parameters
Name	Description
control
IControl
	The IControl to remove.
Returns
Map: Returns itself to allow for method chaining.
Example

// Define a new navigation control.
const navigation = new mapboxgl.NavigationControl();
// Add zoom and rotation controls to the map.
map.addControl(navigation);
// Remove zoom and rotation controls from the map.
map.removeControl(navigation);

Checks if a control is on the map.
Parameters
Name	Description
control
IControl
	The IControl to check.
Returns
boolean: True if map contains control.
Example

// Define a new navigation control.
const navigation = new mapboxgl.NavigationControl();
// Add zoom and rotation controls to the map.
map.addControl(navigation);
// Check that the navigation control exists on the map.
const added = map.hasControl(navigation);
// added === true

Returns the map's containing HTML element.
Returns
HTMLElement: The map's container.
Example

const container = map.getContainer();

Returns the HTML element containing the map's <canvas> element.

If you want to add non-GL overlays to the map, you should append them to this element.

This is the element to which event bindings for map interactivity (such as panning and zooming) are attached. It will receive bubbled events from child elements such as the <canvas>, but not from map controls.
Returns
HTMLElement: The container of the map's <canvas> .
Example

const canvasContainer = map.getCanvasContainer();

Related

    Example: Create a draggable point
    Example: Highlight features within a bounding box 

Returns the map's <canvas> element.
Returns
HTMLCanvasElement: The map's <canvas> element.
Example

const canvas = map.getCanvas();

Related

    Example: Measure distances
    Example: Display a popup on hover
    Example: Center the map on a clicked symbol 

Map constraints

Resizes the map according to the dimensions of its container element.

Checks if the map container size changed and updates the map if it has changed. This method must be called after the map's container is resized programmatically or when the map is shown after being initially hidden with CSS.
Parameters
Name	Description
eventData
(Object | null)
	Additional properties to be passed to movestart , move , resize , and moveend events that get triggered as a result of resize. This can be useful for differentiating the source of an event (for example, user-initiated or programmatically-triggered events).
Returns
Map: Returns itself to allow for method chaining.
Example

// Resize the map when the map container is shown
// after being initially hidden with CSS.
const mapDiv = document.getElementById('map');
if (mapDiv.style.visibility === true) map.resize();

Returns the map's geographical bounds. When the bearing or pitch is non-zero, the visible region is not an axis-aligned rectangle, and the result is the smallest bounds that encompasses the visible region. If a padding is set on the map, the bounds returned are for the inset. With globe projection, the smallest bounds encompassing the visible region may not precisely represent the visible region due to the earth's curvature.
Returns
LngLatBounds: The geographical bounds of the map as LngLatBounds .
Example

const bounds = map.getBounds();

Returns the maximum geographical bounds the map is constrained to, or null if none set.
Returns
Map: The map object.
Example

const maxBounds = map.getMaxBounds();

Sets or clears the map's geographical bounds.

Pan and zoom operations are constrained within these bounds. If a pan or zoom is performed that would display regions outside these bounds, the map will instead display a position and zoom level as close as possible to the operation's request while still remaining within the bounds.

For mercator projection, the viewport will be constrained to the bounds. For other projections such as globe, only the map center will be constrained.
Parameters
Name	Description
bounds
(LngLatBoundsLike | null | undefined)
	The maximum bounds to set. If null or undefined is provided, the function removes the map's maximum bounds.
Returns
Map: Returns itself to allow for method chaining.
Example

// Define bounds that conform to the `LngLatBoundsLike` object.
const bounds = [
    [-74.04728, 40.68392], // [west, south]
    [-73.91058, 40.87764]  // [east, north]
];
// Set the map's max bounds.
map.setMaxBounds(bounds);

Sets or clears the map's minimum zoom level. If the map's current zoom level is lower than the new minimum, the map will zoom to the new minimum.

It is not always possible to zoom out and reach the set minZoom. Other factors such as map height may restrict zooming. For example, if the map is 512px tall it will not be possible to zoom below zoom 0 no matter what the minZoom is set to.
Parameters
Name	Description
minZoom
(number | null | undefined)
	The minimum zoom level to set (-2 - 24). If null or undefined is provided, the function removes the current minimum zoom and it will be reset to -2.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setMinZoom(12.25);

Returns the map's minimum allowable zoom level.
Returns
number: Returns minZoom .
Example

const minZoom = map.getMinZoom();

Sets or clears the map's maximum zoom level. If the map's current zoom level is higher than the new maximum, the map will zoom to the new maximum.
Parameters
Name	Description
maxZoom
(number | null | undefined)
	The maximum zoom level to set. If null or undefined is provided, the function removes the current maximum zoom (sets it to 22).
Returns
Map: Returns itself to allow for method chaining.
Example

map.setMaxZoom(18.75);

Returns the map's maximum allowable zoom level.
Returns
number: Returns maxZoom .
Example

const maxZoom = map.getMaxZoom();

Sets or clears the map's minimum pitch. If the map's current pitch is lower than the new minimum, the map will pitch to the new minimum.
Parameters
Name	Description
minPitch
(number | null | undefined)
	The minimum pitch to set (0-85). If null or undefined is provided, the function removes the current minimum pitch and resets it to 0.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setMinPitch(5);

Returns the map's minimum allowable pitch.
Returns
number: Returns minPitch .
Example

const minPitch = map.getMinPitch();

Sets or clears the map's maximum pitch. If the map's current pitch is higher than the new maximum, the map will pitch to the new maximum.
Parameters
Name	Description
maxPitch
(number | null | undefined)
	The maximum pitch to set. If null or undefined is provided, the function removes the current maximum pitch (sets it to 85).
Returns
Map: Returns itself to allow for method chaining.
Example

map.setMaxPitch(70);

Returns the map's maximum allowable pitch.
Returns
number: Returns maxPitch .
Example

const maxPitch = map.getMaxPitch();

Returns the state of renderWorldCopies. If true, multiple copies of the world will be rendered side by side beyond -180 and 180 degrees longitude. If set to false:

    When the map is zoomed out far enough that a single representation of the world does not fill the map's entire container, there will be blank space beyond 180 and -180 degrees longitude.
    Features that cross 180 and -180 degrees longitude will be cut in two (with one portion on the right edge of the map and the other on the left edge of the map) at every zoom level.

Returns
boolean: Returns renderWorldCopies boolean.
Example

const worldCopiesRendered = map.getRenderWorldCopies();

Related

    Example: Render world copies 

Sets the state of renderWorldCopies.
Parameters
Name	Description
renderWorldCopies
boolean
	If true , multiple copies of the world will be rendered side by side beyond -180 and 180 degrees longitude. If set to false :

    When the map is zoomed out far enough that a single representation of the world does not fill the map's entire container, there will be blank space beyond 180 and -180 degrees longitude.
    Features that cross 180 and -180 degrees longitude will be cut in two (with one portion on the right edge of the map and the other on the left edge of the map) at every zoom level.

undefined is treated as true, null is treated as false.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setRenderWorldCopies(true);

Related

    Example: Render world copies 

Point conversion

Returns a projection object that defines the current map projection.
Returns
ProjectionSpecification: The projection defining the current map projection.
Example

const projection = map.getProjection();

Sets the map's projection. If called with null or undefined, the map will reset to Mercator.
Parameters
Name	Description
projection
(ProjectionSpecification | string | null | undefined)
	The projection that the map should be rendered in. This can be a projection object or a string of the projection's name.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setProjection('albers');
map.setProjection({
    name: 'albers',
    center: [35, 55],
    parallels: [20, 60]
});

Related

    Example: Display a web map using an alternate projection
    Example: Use different map projections for web maps 

Returns a Point representing pixel coordinates, relative to the map's container, that correspond to the specified geographical location.

When the map is pitched and lnglat is completely behind the camera, there are no pixel coordinates corresponding to that location. In that case, the x and y components of the returned Point are set to Number.MAX_VALUE.
Parameters
Name	Description
lnglat
LngLatLike
	The geographical location to project.
altitude
number
	(optional) altitude above the map plane in meters.
Returns
Point: The Point corresponding to lnglat , relative to the map's container .
Example

const coordinate = [-122.420679, 37.772537];
const point = map.project(coordinate);

Returns a LngLat representing geographical coordinates that correspond to the specified pixel coordinates. If horizon is visible, and specified pixel is above horizon, returns a LngLat corresponding to point on horizon, nearest to the point.
Parameters
Name	Description
point
PointLike
	The pixel coordinates to unproject.
altitude
number
	(optional) altitude above the map plane in meters.
Returns
LngLat: The LngLat corresponding to point .
Example

map.on('click', (e) => {
    // When the map is clicked, get the geographic coordinate.
    const coordinate = map.unproject(e.point);
});

Movement state

Returns true if the map is panning, zooming, rotating, or pitching due to a camera animation or user gesture.
Returns
boolean: True if the map is moving.
Example

const isMoving = map.isMoving();

Returns true if the map is zooming due to a camera animation or user gesture.
Returns
boolean: True if the map is zooming.
Example

const isZooming = map.isZooming();

Returns true if the map is rotating due to a camera animation or user gesture.
Returns
boolean: True if the map is rotating.
Example

map.isRotating();

Working with events

Adds a listener for events of a specified type, optionally limited to features in a specified style layer.
Parameters
Name	Description
type
string
	The event type to listen for. Events compatible with the optional layerId parameter are triggered when the cursor enters a visible portion of the specified layer from outside that layer or outside the map canvas.
Event 	Compatible with layerId
mousedown 	yes
mouseup 	yes
mouseover 	yes
mouseout 	yes
mousemove 	yes
mouseenter 	yes (required)
mouseleave 	yes (required)
preclick 	
click 	yes
dblclick 	yes
contextmenu 	yes
touchstart 	yes
touchend 	yes
touchcancel 	yes
wheel 	
resize 	
remove 	
touchmove 	
movestart 	
move 	
moveend 	
dragstart 	
drag 	
dragend 	
zoomstart 	
zoom 	
zoomend 	
rotatestart 	
rotate 	
rotateend 	
pitchstart 	
pitch 	
pitchend 	
boxzoomstart 	
boxzoomend 	
boxzoomcancel 	
webglcontextlost 	
webglcontextrestored 	
load 	
render 	
idle 	
error 	
data 	
styledata 	
sourcedata 	
dataloading 	
styledataloading 	
sourcedataloading 	
styleimagemissing 	
style.load 	
listener
Function
	The function to be called when the event is fired.
layerIds
(string | Array<string>)
	(optional) The ID(s) of a style layer(s). If you provide a layerId , the listener will be triggered only if its location is within a visible feature in these layers, and the event will have a features property containing an array of the matching features. If you do not provide layerIds , the listener will be triggered by a corresponding event happening anywhere on the map, and the event will not have a features property. Note that many event types are not compatible with the optional layerIds parameter.
Returns
Map: Returns itself to allow for method chaining.
Example

// Set an event listener that will fire
// when the map has finished loading.
map.on('load', () => {
    // Add a new layer.
    map.addLayer({
        id: 'points-of-interest',
        source: {
            type: 'vector',
            url: 'mapbox://mapbox.mapbox-streets-v8'
        },
        'source-layer': 'poi_label',
        type: 'circle',
        paint: {
            // Mapbox Style Specification paint properties
        },
        layout: {
            // Mapbox Style Specification layout properties
        }
    });
});

// Set an event listener that will fire
// when a feature on the countries layer of the map is clicked.
map.on('click', 'countries', (e) => {
    new mapboxgl.Popup()
        .setLngLat(e.lngLat)
        .setHTML(`Country name: ${e.features[0].properties.name}`)
        .addTo(map);
});

// Set an event listener that will fire
// when a feature on the countries or background layers of the map is clicked.
map.on('click', ['countries', 'background'], (e) => {
    new mapboxgl.Popup()
        .setLngLat(e.lngLat)
        .setHTML(`Country name: ${e.features[0].properties.name}`)
        .addTo(map);
});

Related

    Example: Add 3D terrain to a map
    Example: Center the map on a clicked symbol
    Example: Create a draggable marker
    Example: Create a hover effect
    Example: Display popup on click 

Adds a listener that will be called only once to a specified event type, optionally limited to events occurring on features in a specified style layer.
Parameters
Name	Description
type
string
	The event type to listen for; one of 'mousedown' , 'mouseup' , 'preclick' , 'click' , 'dblclick' , 'mousemove' , 'mouseenter' , 'mouseleave' , 'mouseover' , 'mouseout' , 'contextmenu' , 'touchstart' , 'touchend' , or 'touchcancel' . mouseenter and mouseover events are triggered when the cursor enters a visible portion of the specified layer from outside that layer or outside the map canvas. mouseleave and mouseout events are triggered when the cursor leaves a visible portion of the specified layer, or leaves the map canvas.
layerIds
(string | Array<string>)
	(optional) The ID(s) of a style layer(s). If you provide layerIds , the listener will be triggered only if its location is within a visible feature in these layers, and the event will have a features property containing an array of the matching features. If you do not provide layerIds , the listener will be triggered by a corresponding event happening anywhere on the map, and the event will not have a features property. Note that many event types are not compatible with the optional layerIds parameter.
listener
Function
	The function to be called when the event is fired.
Returns
Map: Returns itself to allow for method chaining.
Example

// Log the coordinates of a user's first map touch.
map.once('touchstart', (e) => {
    console.log(`The first map touch was at: ${e.lnglat}`);
});

// Log the coordinates of a user's first map touch
// on a specific layer.
map.once('touchstart', 'my-point-layer', (e) => {
    console.log(`The first map touch on the point layer was at: ${e.lnglat}`);
});

// Log the coordinates of a user's first map touch
// on specific layers.
map.once('touchstart', ['my-point-layer', 'my-point-layer-2'], (e) => {
    console.log(`The first map touch on the point layer was at: ${e.lnglat}`);
});

Related

    Example: Create a draggable point
    Example: Animate the camera around a point with 3D terrain
    Example: Play map locations as a slideshow 

Removes an event listener previously added with Map#on, optionally limited to layer-specific events.
Parameters
Name	Description
type
string
	The event type previously used to install the listener.
listener
Function
	The function previously installed as a listener.
layerIds
(string | Array<string>)
	(optional) The layer ID(s) previously used to install the listener.
Returns
Map: Returns itself to allow for method chaining.
Example

// Create a function to print coordinates while a mouse is moving.
function onMove(e) {
    console.log(`The mouse is moving: ${e.lngLat}`);
}
// Create a function to unbind the `mousemove` event.
function onUp(e) {
    console.log(`The final coordinates are: ${e.lngLat}`);
    map.off('mousemove', onMove);
}
// When a click occurs, bind both functions to mouse events.
map.on('mousedown', (e) => {
    map.on('mousemove', onMove);
    map.once('mouseup', onUp);
});

Related

    Example: Create a draggable point 

Querying features

Returns an array of GeoJSON Feature objects representing visible features that satisfy the query parameters.
Parameters
Name	Description
geometry
(PointLike | Array<PointLike>)?
	The geometry of the query region in pixels: either a single point or bottom left and top right points describing a bounding box, where the origin is at the top left. Omitting this parameter (by calling Map#queryRenderedFeatures with zero arguments, or with only an options argument) is equivalent to passing a bounding box encompassing the entire map viewport. Only values within the existing viewport are supported.
options
Object?
	Options object.
options.filter
Array?
	A filter to limit query results.
options.layers
Array<string>?
	An array of style layer IDs for the query to inspect. Only features within these layers will be returned. If target and layers are both undefined, the query will inspect all layers and featuresets in the root style, as well as all featuresets in the root style imports.
options.target
TargetDescriptor?
	A query target to inspect. This could be a style layer ID or a FeaturesetDescriptor . Only features within layers referenced by the query target will be returned. If target and layers are both undefined, the query will inspect all layers and featuresets in the root style, as well as all featuresets in the root style imports.
options.validate
boolean
(default true)
	Whether to check if the [options.filter] conforms to the Mapbox GL Style Specification. Disabling validation is a performance optimization that should only be used if you have previously validated the values you will be passing to this function.
Returns
Array<Object>: An array of GeoJSON feature objects .

The properties value of each returned feature object contains the properties of its source feature. For GeoJSON sources, only string and numeric property values are supported. null, Array, and Object values are not supported.

For featuresets in the style imports, each feature includes top-level target and an optional namespace property as defined in TargetFeature. The target property represents the query target associated with the feature, while the optional namespace property is included to prevent feature ID collisions when layers in the query target reference multiple sources.

For layers and featuresets in the root style, each feature includes top-level layer, source, and sourceLayer properties. The layer property is an object representing the style layer to which the feature belongs. Layout and paint properties in this object contain values which are fully evaluated for the given zoom level and feature.

Only features that are currently rendered are included. Some features will not be included, like:

    Features from layers whose visibility property is "none".
    Features from layers whose zoom range excludes the current zoom level.
    Symbol features that have been hidden due to text or icon collision.

Features from all other layers are included, including features that may have no visible contribution to the rendered result; for example, because the layer's opacity or color alpha component is set to 0.

The topmost rendered feature appears first in the returned array, and subsequent features are sorted by descending z-order. Features that are rendered multiple times (due to wrapping across the antimeridian at low zoom levels) are returned only once (though subject to the following caveat).

Because features come from tiled vector data or GeoJSON data that is converted to tiles internally, feature geometries may be split or duplicated across tile boundaries and, as a result, features may appear multiple times in query results. For example, suppose there is a highway running through the bounding rectangle of a query. The results of the query will be those parts of the highway that lie within the map tiles covering the bounding rectangle, even if the highway extends into other tiles, and the portion of the highway within each map tile will be returned as a separate feature. Similarly, a point feature near a tile boundary may appear in multiple tiles due to tile buffering.

For model layers, id or a property "id" is required to be specified per feature in the source.
Example

// Find all features at a point
const features = map.queryRenderedFeatures(
  [20, 35],
  {target: {layerId: 'my-layer-name'}}
);

// Find all features within a static bounding box
const features = map.queryRenderedFeatures(
  [[10, 20], [30, 50]],
  {target: {layerId: 'my-layer-name'}}
);

// Find all features within a bounding box around a point
const width = 10;
const height = 20;
const features = map.queryRenderedFeatures([
    [point.x - width / 2, point.y - height / 2],
    [point.x + width / 2, point.y + height / 2]
], {target: {layerId: 'my-layer-name'}});

// Query all rendered features from a single layer
const features = map.queryRenderedFeatures({target: {layerId: 'my-layer-name'}});

// ...or
const features = map.queryRenderedFeatures({layers: ['my-layer-name']});

// Query all rendered features from a `poi` featureset in the `basemap` style import
const features = map.queryRenderedFeatures({target: {featuresetId: 'poi', importId: 'basemap'}});

Related

    Example: Get features under the mouse pointer
    Example: Highlight features within a bounding box
    Example: Filter features within map view 

Returns an array of GeoJSON Feature objects representing features within the specified vector tile or GeoJSON source that satisfy the query parameters.
Parameters
Name	Description
sourceId
string
	The ID of the vector tile or GeoJSON source to query.
parameters
Object?
	Options object.
parameters.filter
Array?
	A filter to limit query results.
parameters.sourceLayer
string?
	The name of the source layer to query. For vector tile sources, this parameter is required. For GeoJSON sources, it is ignored.
parameters.validate
boolean
(default true)
	Whether to check if the [parameters.filter] conforms to the Mapbox GL Style Specification. Disabling validation is a performance optimization that should only be used if you have previously validated the values you will be passing to this function.
Returns
Array<Object>: An array of GeoJSON Feature objects .

In contrast to Map#queryRenderedFeatures, this function returns all features matching the query parameters, whether or not they are rendered by the current style (in other words, are visible). The domain of the query includes all currently-loaded vector tiles and GeoJSON source tiles: this function does not check tiles outside the currently visible viewport.

Because features come from tiled vector data or GeoJSON data that is converted to tiles internally, feature geometries may be split or duplicated across tile boundaries and, as a result, features may appear multiple times in query results. For example, suppose there is a highway running through the bounding rectangle of a query. The results of the query will be those parts of the highway that lie within the map tiles covering the bounding rectangle, even if the highway extends into other tiles, and the portion of the highway within each map tile will be returned as a separate feature. Similarly, a point feature near a tile boundary may appear in multiple tiles due to tile buffering.
Example

// Find all features in one source layer in a vector source
const features = map.querySourceFeatures('your-source-id', {
    sourceLayer: 'your-source-layer'
});

Related

    Example: Highlight features containing similar data 

Determines if the given point is located on a visible map surface.
Parameters
Name	Description
point
PointLike
	The point to be checked, specified as an array of two numbers representing the x and y coordinates, or as a Point object.
Returns
boolean: Returns true if the point is on the visible map surface, otherwise returns false .
Example

const pointOnSurface = map.isPointOnSurface([100, 200]);

Gets the state of cooperativeGestures.
Returns
boolean: Returns the cooperativeGestures boolean.
Example

const cooperativeGesturesEnabled = map.getCooperativeGestures();

Sets the state of cooperativeGestures.
Parameters
Name	Description
enabled
boolean
	If true , scroll zoom will require pressing the ctrl or ⌘ key while scrolling to zoom map, and touch pan will require using two fingers while panning to move the map. Touch pitch will require three fingers to activate if enabled.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setCooperativeGestures(true);

Working with styles

Updates the map's Mapbox style object with a new value.

If a style is already set when this is used and the diff option is set to true, the map renderer will attempt to compare the given style against the map's current state and perform only the changes necessary to make the map style match the desired state. Changes in sprites (images used for icons and patterns) and glyphs (fonts for label text) cannot be diffed. If the sprites or fonts used in the current style and the given style are different in any way, the map renderer will force a full update, removing the current style and building the given one from scratch.
Parameters
Name	Description
style
(Object | string | null)
	A JSON object conforming to the schema described in the Mapbox Style Specification , or a URL to such JSON.
options
Object?
	Options object.
options.config
Object
(default null)
	The initial configuration options for the style fragments. Each key in the object is a fragment ID (e.g., basemap ) and each value is a configuration object.
options.diff
boolean
(default true)
	If false, force a 'full' update, removing the current style and building the given one instead of attempting a diff-based update.
options.localIdeographFontFamily
string
(default 'sans-serif')
	Defines a CSS font-family for locally overriding generation of glyphs in the 'CJK Unified Ideographs', 'Hiragana', 'Katakana' and 'Hangul Syllables' ranges. In these ranges, font settings from the map's style will be ignored, except for font-weight keywords (light/regular/medium/bold). Set to false , to enable font settings from the map's style for these glyph ranges. Forces a full update.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setStyle("mapbox://styles/mapbox/streets-v11");

map.setStyle("mapbox://styles/mapbox/standard", {
    "config": {
        "basemap": {
            "lightPreset": "night"
        }
    }
});

Related

    Example: Change a map's style 

Returns the map's Mapbox style object, a JSON object which can be used to recreate the map's style.

For the Mapbox Standard style or any "fragment" style (which is a style with fragment: true or a schema property defined), this method returns an empty style with no layers or sources. The original style is wrapped into an import with the ID basemap as a fragment style and is not intended to be used directly. This design ensures that user logic is not tied to style internals, allowing Mapbox to roll out style updates seamlessly and consistently.
Returns
(StyleSpecification | void): The map's style JSON object.
Example

map.on('load', () => {
    const styleJson = map.getStyle();
});

Returns a Boolean indicating whether the map's style is fully loaded.
Returns
boolean: A Boolean indicating whether the style is fully loaded.
Example

const styleLoadStatus = map.isStyleLoaded();

Sources

Adds a source to the map's style.
Parameters
Name	Description
id
string
	The ID of the source to add. Must not conflict with existing sources.
source
Object
	The source object, conforming to the Mapbox Style Specification's source definition or CanvasSourceOptions .
Returns
Map: Returns itself to allow for method chaining.
Example

map.addSource('my-data', {
    type: 'vector',
    url: 'mapbox://myusername.tilesetid'
});

map.addSource('my-data', {
    "type": "geojson",
    "data": {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [-77.0323, 38.9131]
        },
        "properties": {
            "title": "Mapbox DC",
            "marker-symbol": "monument"
        }
    }
});

Related

    Example: Vector source: Show and hide layers
    Example: GeoJSON source: Add live realtime data
    Example: Raster DEM source: Add hillshading 

Returns a Boolean indicating whether the source is loaded. Returns true if the source with the given ID in the map's style has no outstanding network requests, otherwise false.
Parameters
Name	Description
id
string
	The ID of the source to be checked.
Returns
boolean: A Boolean indicating whether the source is loaded.
Example

const sourceLoaded = map.isSourceLoaded('bathymetry-data');

Returns a Boolean indicating whether all tiles in the viewport from all sources on the style are loaded.
Returns
boolean: A Boolean indicating whether all tiles are loaded.
Example

const tilesLoaded = map.areTilesLoaded();

Removes a source from the map's style.
Parameters
Name	Description
id
string
	The ID of the source to remove.
Returns
Map: Returns itself to allow for method chaining.
Example

map.removeSource('bathymetry-data');

Returns the source with the specified ID in the map's style.

This method is often used to update a source using the instance members for the relevant source type as defined in Sources. For example, setting the data for a GeoJSON source or updating the url and coordinates of an image source.
Parameters
Name	Description
id
string
	The ID of the source to get.
Returns
Object?: The style source with the specified ID or undefined if the ID corresponds to no existing sources. The shape of the object varies by source type. A list of options for each source type is available on the Mapbox Style Specification's Sources page.
Example

const sourceObject = map.getSource('points');

Related

    Example: Create a draggable point
    Example: Animate a point
    Example: Add live realtime data 

Images

Add an image to the style. This image can be displayed on the map like any other icon in the style's sprite using the image's ID with icon-image, background-pattern, fill-pattern, or line-pattern. A Map.event:error event will be fired if there is not enough space in the sprite to add this image.
Parameters
Name	Description
id
string
	The ID of the image.
image
(HTMLImageElement | ImageBitmap | ImageData | {width: number, height: number, data: (Uint8Array | Uint8ClampedArray)} | StyleImageInterface)
	The image as an HTMLImageElement , ImageData , ImageBitmap or object with width , height , and data properties with the same format as ImageData .
options
(Object | null)
(default {})
	Options object.
options.content
[number, number, number, number]
	[x1, y1, x2, y2] If icon-text-fit is used in a layer with this image, this option defines the part of the image that can be covered by the content in text-field .
options.pixelRatio
number
(default 1)
	The ratio of pixels in the image to physical pixels on the screen.
options.sdf
boolean
(default false)
	Whether the image should be interpreted as an SDF image.
options.stretchX
Array<[number, number]>
	[[x1, x2], ...] If icon-text-fit is used in a layer with this image, this option defines the part(s) of the image that can be stretched horizontally.
options.stretchY
Array<[number, number]>
	[[y1, y2], ...] If icon-text-fit is used in a layer with this image, this option defines the part(s) of the image that can be stretched vertically.
Example

// If the style's sprite does not already contain an image with ID 'cat',
// add the image 'cat-icon.png' to the style's sprite with the ID 'cat'.
map.loadImage('https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Cat_silhouette.svg/400px-Cat_silhouette.svg.png', (error, image) => {
    if (error) throw error;
    if (!map.hasImage('cat')) map.addImage('cat', image);
});

// Add a stretchable image that can be used with `icon-text-fit`
// In this example, the image is 600px wide by 400px high.
map.loadImage('https://upload.wikimedia.org/wikipedia/commons/8/89/Black_and_White_Boxed_%28bordered%29.png', (error, image) => {
    if (error) throw error;
    if (!map.hasImage('border-image')) {
        map.addImage('border-image', image, {
            content: [16, 16, 300, 384], // place text over left half of image, avoiding the 16px border
            stretchX: [[16, 584]], // stretch everything horizontally except the 16px border
            stretchY: [[16, 384]], // stretch everything vertically except the 16px border
        });
    }
});

Related

    Example: Use HTMLImageElement : Add an icon to the map
    Example: Use ImageData : Add a generated icon to the map 

Update an existing image in a style. This image can be displayed on the map like any other icon in the style's sprite using the image's ID with icon-image, background-pattern, fill-pattern, or line-pattern.
Parameters
Name	Description
id
string
	The ID of the image.
image
(HTMLImageElement | ImageBitmap | ImageData | StyleImageInterface)
	The image as an HTMLImageElement , ImageData , ImageBitmap or object with width , height , and data properties with the same format as ImageData .
Example

// Load an image from an external URL.
map.loadImage('http://placekitten.com/50/50', (error, image) => {
    if (error) throw error;
    // If an image with the ID 'cat' already exists in the style's sprite,
    // replace that image with a new image, 'other-cat-icon.png'.
    if (map.hasImage('cat')) map.updateImage('cat', image);
});

Check whether or not an image with a specific ID exists in the style. This checks both images in the style's original sprite and any images that have been added at runtime using Map#addImage.
Parameters
Name	Description
id
string
	The ID of the image.
Returns
boolean: A Boolean indicating whether the image exists.
Example

// Check if an image with the ID 'cat' exists in
// the style's sprite.
const catIconExists = map.hasImage('cat');

Remove an image from a style. This can be an image from the style's original sprite or any images that have been added at runtime using Map#addImage.
Parameters
Name	Description
id
string
	The ID of the image.
Example

// If an image with the ID 'cat' exists in
// the style's sprite, remove it.
if (map.hasImage('cat')) map.removeImage('cat');

Load an image from an external URL to be used with Map#addImage. External domains must support CORS.
Parameters
Name	Description
url
string
	The URL of the image file. Image file must be in png, webp, or jpg format.
callback
Function
	Expecting callback(error, data) . Called when the image has loaded or with an error argument if there is an error.
Example

// Load an image from an external URL.
map.loadImage('http://placekitten.com/50/50', (error, image) => {
    if (error) throw error;
    // Add the loaded image to the style's sprite with the ID 'kitten'.
    map.addImage('kitten', image);
});

Related

    Example: Add an icon to the map 

Returns an Array of strings containing the IDs of all images currently available in the map. This includes both images from the style's original sprite and any images that have been added at runtime using Map#addImage.
Returns
Array<string>: An Array of strings containing the names of all sprites/images currently available in the map.
Example

const allImages = map.listImages();

Models

Add a model to the style. This model can be displayed on the map like any other model in the style using the model ID in conjunction with a 2D vector layer. This API can also be used for updating a model. If the model for a given modelId was already added, it gets replaced by the new model.
Parameters
Name	Description
id
string
	The ID of the model.
url
string
	Pointing to the model to load.
Example

// If the style does not already contain a model with ID 'tree',
// load a tree model and then use a geojson to show it.
map.addModel('tree', 'http://path/to/my/tree.glb');
map.addLayer({
    "id": "tree-layer",
    "type": "model",
    "source": "trees",
    "source-layer": "trees",
    "layout": {
        "model-id": "tree"
    }
});

Check whether or not a model with a specific ID exists in the style. This checks both models in the style and any models that have been added at runtime using Map#addModel.
Parameters
Name	Description
id
string
	The ID of the model.
Returns
boolean: A Boolean indicating whether the model exists.
Example

// Check if a model with the ID 'tree' exists in
// the style.
const treeModelExists = map.hasModel('tree');

Remove an model from a style. This can be a model from the style original or any models that have been added at runtime using Map#addModel.
Parameters
Name	Description
id
string
	The ID of the model.
Example

// If an model with the ID 'tree' exists in
// the style, remove it.
if (map.hasModel('tree')) map.removeModel('tree');

Returns an Array of strings containing the IDs of all models currently available in the map. This includes both models from the style and any models that have been added at runtime using Map#addModel.
Returns
Array<string>: An Array of strings containing the names of all model IDs currently available in the map.
Example

const allModels = map.listModels();

Layers

Adds a Mapbox style layer to the map's style.

A layer defines how data from a specified source will be styled. Read more about layer types and available paint and layout properties in the Mapbox Style Specification.
Parameters
Name	Description
layer
(Object | CustomLayerInterface)
	The layer to add, conforming to either the Mapbox Style Specification's layer definition or, less commonly, the CustomLayerInterface specification. The Mapbox Style Specification's layer definition is appropriate for most layers.
layer.filter
Array?
	(optional) An expression specifying conditions on source features. Only features that match the filter are displayed. The Mapbox Style Specification includes more information on the limitations of the filter parameter and a complete list of available expressions . If no filter is provided, all features in the source (or source layer for vector tilesets) will be displayed.
layer.id
string
	A unique identifier that you define.
layer.layout
Object?
	(optional) Layout properties for the layer. Available layout properties vary by layer.type . A full list of layout properties for each layer type is available in the Mapbox Style Specification . If no layout properties are specified, default values will be used.
layer.maxzoom
number?
	(optional) The maximum zoom level for the layer. At zoom levels equal to or greater than the maxzoom, the layer will be hidden. The value can be any number between 0 and 24 (inclusive). If no maxzoom is provided, the layer will be visible at all zoom levels for which there are tiles available.
layer.metadata
Object?
	(optional) Arbitrary properties useful to track with the layer, but do not influence rendering.
layer.minzoom
number?
	(optional) The minimum zoom level for the layer. At zoom levels less than the minzoom, the layer will be hidden. The value can be any number between 0 and 24 (inclusive). If no minzoom is provided, the layer will be visible at all zoom levels for which there are tiles available.
layer.paint
Object?
	(optional) Paint properties for the layer. Available paint properties vary by layer.type . A full list of paint properties for each layer type is available in the Mapbox Style Specification . If no paint properties are specified, default values will be used.
layer.renderingMode
string?
	This is only applicable for layers with the type custom . See CustomLayerInterface for more information.
layer.slot
string?
	(optional) The identifier of a slot layer that will be used to position this style layer. A slot layer serves as a predefined position in the layer order for inserting associated layers. Note : During 3D globe and terrain rendering, GL JS aims to batch multiple layers together for optimal performance. This process might lead to a rearrangement of layers. Layers draped over globe and terrain, such as fill , line , background , hillshade , and raster , are rendered first. These layers are rendered underneath symbols, regardless of whether they are placed in the middle or top slots or without a designated slot.
layer.source
(string | Object)?
	The data source for the layer. Reference a source that has already been defined using the source's unique id. Reference a new source using a source object (as defined in the Mapbox Style Specification ) directly. This is required for all layer.type options except for custom and background .
layer.sourceLayer
string?
	(optional) The name of the source layer within the specified layer.source to use for this style layer. This is only applicable for vector tile sources and is required when layer.source is of the type vector .
layer.type
string
	The type of layer (for example fill or symbol ). A list of layer types is available in the Mapbox Style Specification .

This can also be custom. For more information, see CustomLayerInterface.
beforeId
string?
	The ID of an existing layer to insert the new layer before, resulting in the new layer appearing visually beneath the existing layer. If this argument is not specified, the layer will be appended to the end of the layers array and appear visually above all other layers. Note : Layers can only be rearranged within the same slot . The new layer must share the same slot as the existing layer to be positioned underneath it. If the layers are in different slots, the beforeId parameter will be ignored and the new layer will be appended to the end of the layers array. During 3D globe and terrain rendering, GL JS aims to batch multiple layers together for optimal performance. This process might lead to a rearrangement of layers. Layers draped over globe and terrain, such as fill , line , background , hillshade , and raster , are rendered first. These layers are rendered underneath symbols, regardless of whether they are placed in the middle or top slots or without a designated slot.
Returns
Map: Returns itself to allow for method chaining.
Example

// Add a circle layer with a vector source
map.addLayer({
    id: 'points-of-interest',
    source: {
        type: 'vector',
        url: 'mapbox://mapbox.mapbox-streets-v8'
    },
    'source-layer': 'poi_label',
    type: 'circle',
    paint: {
    // Mapbox Style Specification paint properties
    },
    layout: {
    // Mapbox Style Specification layout properties
    }
});

// Define a source before using it to create a new layer
map.addSource('state-data', {
    type: 'geojson',
    data: 'path/to/data.geojson'
});

map.addLayer({
    id: 'states',
    // References the GeoJSON source defined above
    // and does not require a `source-layer`
    source: 'state-data',
    type: 'symbol',
    layout: {
        // Set the label content to the
        // feature's `name` property
        'text-field': ['get', 'name']
    }
});

// Add a new symbol layer to a slot
map.addLayer({
    id: 'states',
    // References a source that's already been defined
    source: 'state-data',
    type: 'symbol',
    // Add the layer to the existing `top` slot
    slot: 'top',
    layout: {
        // Set the label content to the
        // feature's `name` property
        'text-field': ['get', 'name']
    }
});

// Add a new symbol layer before an existing layer
map.addLayer({
    id: 'states',
    // References a source that's already been defined
    source: 'state-data',
    type: 'symbol',
    layout: {
        // Set the label content to the
        // feature's `name` property
        'text-field': ['get', 'name']
    }
// Add the layer before the existing `cities` layer
}, 'cities');

Related

    Example: Select features around a clicked point (fill layer)
    Example: Add a new layer below labels
    Example: Create and style clusters (circle layer)
    Example: Add a vector tile source (line layer)
    Example: Add a WMS layer (raster layer) 

Returns current slot of the layer.
Parameters
Name	Description
layerId
string
	Identifier of the layer to retrieve its current slot.
Returns
(string | null): The slot identifier or null if layer doesn't have it.
Example

map.getSlot('roads');

Sets or removes a slot of style layer.
Parameters
Name	Description
layerId
string
	Identifier of style layer.
slot
string
	Identifier of slot. If null or undefined is provided, the method removes slot.
Returns
Map: Returns itself to allow for method chaining.
Example

// Sets new slot for style layer
map.setSlot("heatmap", "top");

Adds new import to current style.
Parameters
Name	Description
importSpecification
ImportSpecification
	Specification of import.
beforeId
string
	(optional) Identifier of an existing import to insert the new import before.
Returns
Map: Returns itself to allow for method chaining.
Example

// Add streets style to empty map
new Map({style: {version: 8, sources: {}, layers: []}})
    .addImport({id: 'basemap', url: 'mapbox://styles/mapbox/streets-v12'});

// Add new style before already added
const map = new Map({
    imports: [
        {
            id: 'basemap',
            url: 'mapbox://styles/mapbox/standard'
        }
    ],
    style: {
        version: 8,
        sources: {},
        layers: []
    }
});

map.addImport({
    id: 'lakes',
    url: 'https://styles/mapbox/streets-v12'
}, 'basemap');

Updates already added to style import.
Parameters
Name	Description
importId
string
	Identifier of import to update.
importSpecification
(ImportSpecification | string)
	Import specification or URL of style.
Returns
Map: Returns itself to allow for method chaining.
Example

// Update import with new data
map.updateImport('basemap', {
    data: {
        version: 8,
        sources: {},
        layers: [
            {
                id: 'background',
                type: 'background',
                paint: {
                    'background-color': '#eee'
                }
            }
        ]
    }
});

// Change URL of imported style
map.updateImport('basemap', 'mapbox://styles/mapbox/other-standard');

Removes added to style import.
Parameters
Name	Description
importId
string
	Identifier of import to remove.
Returns
Map: Returns itself to allow for method chaining.
Example

// Removes imported style
map.removeImport('basemap');

Moves import to position before another import, specified with beforeId. Order of imported styles corresponds to order of their layers.
Parameters
Name	Description
importId
string
	Identifier of import to move.
beforeId
string
	The identifier of an existing import to move the new import before.
Returns
Map: Returns itself to allow for method chaining.
Example

const map = new Map({
    style: {
        imports: [
            {
                id: 'basemap',
                url: 'mapbox://styles/mapbox/standard'
            },
            {
                id: 'streets-v12',
                url: 'mapbox://styles/mapbox/streets-v12'
            }
        ]
    }
});
// Place `streets-v12` import before `basemap`
map.moveImport('streets-v12', 'basemap');

Moves a layer to a different z-position.
Parameters
Name	Description
id
string
	The ID of the layer to move.
beforeId
string?
	The ID of an existing layer to insert the new layer before. When viewing the map, the id layer will appear beneath the beforeId layer. If beforeId is omitted, the layer will be appended to the end of the layers array and appear above all other layers on the map. Note : Layers can only be rearranged within the same slot . The new layer must share the same slot as the existing layer to be positioned underneath it. If the layers are in different slots, the beforeId parameter will be ignored and the new layer will be appended to the end of the layers array. During 3D globe and terrain rendering, GL JS aims to batch multiple layers together for optimal performance. This process might lead to a rearrangement of layers. Layers draped over globe and terrain, such as fill , line , background , hillshade , and raster , are rendered first. These layers are rendered underneath symbols, regardless of whether they are placed in the middle or top slots or without a designated slot.
Returns
Map: Returns itself to allow for method chaining.
Example

// Move a layer with ID 'polygon' before the layer with ID 'country-label'. The `polygon` layer will appear beneath the `country-label` layer on the map.
map.moveLayer('polygon', 'country-label');

Removes the layer with the given ID from the map's style.

If no such layer exists, an error event is fired.
Parameters
Name	Description
id
string
	ID of the layer to remove.
Returns
Map: Returns itself to allow for method chaining.
Example

// If a layer with ID 'state-data' exists, remove it.
if (map.getLayer('state-data')) map.removeLayer('state-data');

Fires
Map.event:error

Returns the layer with the specified ID in the map's style.
Parameters
Name	Description
id
string
	The ID of the layer to get.
Returns
Object?: The layer with the specified ID, or undefined if the ID corresponds to no existing layers.
Example

const stateDataLayer = map.getLayer('state-data');

Related

    Example: Filter symbols by toggling a list
    Example: Filter symbols by text input 

Returns the IDs of all slots in the map's style.
Returns
Array<string>: The IDs of all slots in the map's style.
Example

const slots = map.getSlots();

Sets the zoom extent for the specified style layer. The zoom extent includes the minimum zoom level and maximum zoom level) at which the layer will be rendered.

Note: For style layers using vector sources, style layers cannot be rendered at zoom levels lower than the minimum zoom level of the source layer because the data does not exist at those zoom levels. If the minimum zoom level of the source layer is higher than the minimum zoom level defined in the style layer, the style layer will not be rendered at all zoom levels in the zoom range.
Parameters
Name	Description
layerId
string
	The ID of the layer to which the zoom extent will be applied.
minzoom
number
	The minimum zoom to set (0-24).
maxzoom
number
	The maximum zoom to set (0-24).
Returns
Map: Returns itself to allow for method chaining.
Example

map.setLayerZoomRange('my-layer', 2, 5);

Sets the filter for the specified style layer.

Filters control which features a style layer renders from its source. Any feature for which the filter expression evaluates to true will be rendered on the map. Those that are false will be hidden.

Use setFilter to show a subset of your source data.

To clear the filter, pass null or undefined as the second parameter.
Parameters
Name	Description
layerId
string
	The ID of the layer to which the filter will be applied.
filter
(Array | null | undefined)
	The filter, conforming to the Mapbox Style Specification's filter definition . If null or undefined is provided, the function removes any existing filter from the layer.
options
Object?
(default {})
	Options object.
options.validate
boolean
(default true)
	Whether to check if the filter conforms to the Mapbox GL Style Specification. Disabling validation is a performance optimization that should only be used if you have previously validated the values you will be passing to this function.
Returns
Map: Returns itself to allow for method chaining.
Example

// display only features with the 'name' property 'USA'
map.setFilter('my-layer', ['==', ['get', 'name'], 'USA']);

// display only features with five or more 'available-spots'
map.setFilter('bike-docks', ['>=', ['get', 'available-spots'], 5]);

// remove the filter for the 'bike-docks' style layer
map.setFilter('bike-docks', null);

Related

    Example: Filter features within map view
    Example: Highlight features containing similar data
    Example: Create a timeline animation
    Tutorial: Show changes over time 

Returns the filter applied to the specified style layer.
Parameters
Name	Description
layerId
string
	The ID of the style layer whose filter to get.
Returns
Array: The layer's filter.
Example

const filter = map.getFilter('myLayer');

Sets the value of a paint property in the specified style layer.
Parameters
Name	Description
layerId
string
	The ID of the layer to set the paint property in.
name
string
	The name of the paint property to set.
value
any
	The value of the paint property to set. Must be of a type appropriate for the property, as defined in the Mapbox Style Specification .
options
Object?
(default {})
	Options object.
options.validate
boolean
(default true)
	Whether to check if value conforms to the Mapbox GL Style Specification. Disabling validation is a performance optimization that should only be used if you have previously validated the values you will be passing to this function.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setPaintProperty('my-layer', 'fill-color', '#faafee');

Related

    Example: Change a layer's color with buttons
    Example: Adjust a layer's opacity
    Example: Create a draggable point 

Returns the value of a paint property in the specified style layer.
Parameters
Name	Description
layerId
string
	The ID of the layer to get the paint property from.
name
string
	The name of a paint property to get.
Returns
any: The value of the specified paint property.
Example

const paintProperty = map.getPaintProperty('mySymbolLayer', 'icon-color');

Sets the value of a layout property in the specified style layer.
Parameters
Name	Description
layerId
string
	The ID of the layer to set the layout property in.
name
string
	The name of the layout property to set.
value
any
	The value of the layout property. Must be of a type appropriate for the property, as defined in the Mapbox Style Specification .
options
Object?
(default {})
	Options object.
options.validate
boolean
(default true)
	Whether to check if value conforms to the Mapbox GL Style Specification. Disabling validation is a performance optimization that should only be used if you have previously validated the values you will be passing to this function.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setLayoutProperty('my-layer', 'visibility', 'none');

Related

    Example: Show and hide layers 

Returns the value of a layout property in the specified style layer.
Parameters
Name	Description
layerId
string
	The ID of the layer to get the layout property from.
name
string
	The name of the layout property to get.
Returns
any: The value of the specified layout property.
Example

const layoutProperty = map.getLayoutProperty('mySymbolLayer', 'icon-anchor');

Sets the value of a layout or paint property in the specified style layer.
Parameters
Name	Description
layerId
string
	The ID of the layer to set the layout or paint property in.
name
string
	The name of the layout or paint property to set.
value
any
	The value of the layout or paint property. Must be of a type appropriate for the property, as defined in the Mapbox Style Specification .
options
Object?
(default {})
	Options object.
options.validate
boolean
(default true)
	Whether to check if value conforms to the Mapbox GL Style Specification. Disabling validation is a performance optimization that should only be used if you have previously validated the values you will be passing to this function.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setLayerProperty('my-layer', 'visibility', 'none');

Style properties

Returns the glyphs URL of the current style.
Returns
string: Returns a glyph URL template.
Example

map.getGlyphsUrl();

Sets a URL template for loading signed-distance-field glyph sets in PBF format. The URL must include {fontstack} and {range} tokens.
Parameters
Name	Description
url
string
	A URL template for loading SDF glyph sets in PBF format.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setGlyphsUrl('mapbox://fonts/mapbox/{fontstack}/{range}.pbf');

Returns the imported style configuration.
Parameters
Name	Description
importId
string
	The name of the imported style (e.g. basemap ).
Returns
any: Returns the imported style configuration.
Example

map.getConfig('basemap');

Sets the imported style configuration value.
Parameters
Name	Description
importId
string
	The name of the imported style (e.g. basemap ).
config
ConfigSpecification
	The imported style configuration value.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setConfig('basemap', {lightPreset: 'night', showPointOfInterestLabels: false});

Returns the value of a configuration property in the imported style.
Parameters
Name	Description
importId
string
	The name of the imported style (e.g. basemap ).
configName
string
	The name of the configuration property from the style.
Returns
any: Returns the value of the configuration property.
Example

map.getConfigProperty('basemap', 'showLabels');

Sets the value of a configuration property in the currently set style.
Parameters
Name	Description
importId
string
	The name of the imported style to set the config for (e.g. basemap ).
configName
string
	The name of the configuration property from the style.
value
any
	The value of the configuration property. Must be of a type appropriate for the property, as defined by the style configuration schema.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setConfigProperty('basemap', 'showLabels', false);

Adds a set of Mapbox style light to the map's style.

Note: This light is not to confuse with our legacy light API used through Map#setLight and Map#getLight.
Parameters
Name	Description
lights
Array<LightsSpecification>
	An array of lights to add, conforming to the Mapbox Style Specification's light definition.
Returns
Map: Returns itself to allow for method chaining.
Example

// Add a directional light
map.setLights([{
    "id": "sun_light",
    "type": "directional",
    "properties": {
        "color": "rgba(255.0, 0.0, 0.0, 1.0)",
        "intensity": 0.4,
        "direction": [200.0, 40.0],
        "cast-shadows": true,
        "shadow-intensity": 0.2
    }
}]);

Returns the lights added to the map.
Returns
Array<LightSpecification>: Lights added to the map.
Example

const lights = map.getLights();

Sets the any combination of light values.

_Note: that this API is part of the legacy light API, prefer using Map#setLights.
Parameters
Name	Description
light
LightSpecification
	Light properties to set. Must conform to the Light Style Specification .
options
Object?
(default {})
	Options object.
options.validate
boolean
(default true)
	Whether to check if the filter conforms to the Mapbox GL Style Specification. Disabling validation is a performance optimization that should only be used if you have previously validated the values you will be passing to this function.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setLight({
    "anchor": "viewport",
    "color": "blue",
    "intensity": 0.5
});

Returns the value of the light object.
Returns
LightSpecification: Light properties of the style.
Example

const light = map.getLight();

Sets the terrain property of the style.
Parameters
Name	Description
terrain
TerrainSpecification
	Terrain properties to set. Must conform to the Terrain Style Specification . If null or undefined is provided, function removes terrain. Exaggeration could be updated for the existing terrain without explicitly specifying the source .
Returns
Map: Returns itself to allow for method chaining.
Example

map.addSource('mapbox-dem', {
    'type': 'raster-dem',
    'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
    'tileSize': 512,
    'maxzoom': 14
});
// add the DEM source as a terrain layer with exaggerated height
map.setTerrain({'source': 'mapbox-dem', 'exaggeration': 1.5});
// update the exaggeration for the existing terrain
map.setTerrain({'exaggeration': 2});

Returns the terrain specification or null if terrain isn't set on the map.
Returns
(TerrainSpecification | null): Terrain specification properties of the style.
Example

const terrain = map.getTerrain();

Sets the fog property of the style.
Parameters
Name	Description
fog
FogSpecification
	The fog properties to set. Must conform to the Fog Style Specification . If null or undefined is provided, this function call removes the fog from the map.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setFog({
    "range": [0.8, 8],
    "color": "#dc9f9f",
    "horizon-blend": 0.5,
    "high-color": "#245bde",
    "space-color": "#000000",
    "star-intensity": 0.15
});

Related

    Example: Add fog to a map 

Returns the fog specification or null if fog is not set on the map.
Returns
FogSpecification: Fog specification properties of the style.
Example

const fog = map.getFog();

Sets the color-theme property of the style.
Parameters
Name	Description
colorTheme
ColorThemeSpecification
	The color-theme properties to set. If null or undefined is provided, this function call removes the color-theme from the map. Note: Calling this function triggers a full reload of tiles.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setColorTheme({
    "data": "iVBORw0KGgoAA..."
});

Sets the color-theme property of an import, which overrides the color-theme property of the imported style data.
Parameters
Name	Description
importId
string
	Identifier of import to update.
colorTheme
ColorThemeSpecification
	The color-theme properties to set. If null or undefined is provided, this function call removes the color-theme override. Note: Calling this function triggers a full reload of tiles.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setImportColorTheme("someImportId", {
    "data": "iVBORw0KGgoAA..."
});

Sets the camera property of the style.
Parameters
Name	Description
camera
CameraSpecification
	The camera properties to set. Must conform to the Camera Style Specification.
Returns
Map: Returns itself to allow for method chaining.
Example

map.setCamera({
    "camera-projection": "perspective",
});

Returns the camera options specification.
Returns
CameraSpecification: Camera specification properties of the style.
Example

const camera = map.getCamera();

Feature state

Sets the state of a feature. A feature's state is a set of user-defined key-value pairs that are assigned to a feature at runtime. When using this method, the state object is merged with any existing key-value pairs in the feature's state. Features are identified by their id attribute, which can be any number or string.

This method can only be used with sources that have a id attribute. The id attribute can be defined in three ways:

    For vector or GeoJSON sources, including an id attribute in the original data file.
    For vector or GeoJSON sources, using the promoteId option at the time the source is defined.
    For GeoJSON sources, using the generateId option to auto-assign an id based on the feature's index in the source data. If you change feature data using map.getSource('some id').setData(...), you may need to re-apply state taking into account updated id values.

Note: You can use the feature-state expression to access the values in a feature's state object for the purposes of styling.
Parameters
Name	Description
feature
Object
	Feature identifier. Feature objects returned from Map#queryRenderedFeatures or event handlers can be used as feature identifiers.
feature.id
(number | string)
	Unique id of the feature. Can be an integer or a string, but supports string values only when the promoteId option has been applied to the source or the string can be cast to an integer.
feature.source
string
	The id of the vector or GeoJSON source for the feature.
feature.sourceLayer
string?
	(optional) For vector tile sources, sourceLayer is required .
state
Object
	A set of key-value pairs. The values should be valid JSON types.
Returns
Map: The map object.
Example

// When the mouse moves over the `my-layer` layer, update
// the feature state for the feature under the mouse
map.on('mousemove', 'my-layer', (e) => {
    if (e.features.length > 0) {
        map.setFeatureState({
            source: 'my-source',
            sourceLayer: 'my-source-layer',
            id: e.features[0].id,
        }, {
            hover: true
        });
    }
});

Related

    Example: Create a hover effect
    Tutorial: Create interactive hover effects with Mapbox GL JS 

Removes the state of a feature, setting it back to the default behavior. If only a feature.source is specified, it will remove the state for all features from that source. If feature.id is also specified, it will remove all keys for that feature's state. If key is also specified, it removes only that key from that feature's state. Features are identified by their feature.id attribute, which can be any number or string.
Parameters
Name	Description
feature
Object
	Identifier of where to remove state. It can be a source, a feature, or a specific key of feature. Feature objects returned from Map#queryRenderedFeatures or event handlers can be used as feature identifiers.
feature.id
(number | string)?
	(optional) Unique id of the feature. Can be an integer or a string, but supports string values only when the promoteId option has been applied to the source or the string can be cast to an integer.
feature.source
string
	The id of the vector or GeoJSON source for the feature.
feature.sourceLayer
string?
	(optional) For vector tile sources, sourceLayer is required.
key
string?
	(optional) The key in the feature state to reset.
Returns
this
Example

// Reset the entire state object for all features
// in the `my-source` source
map.removeFeatureState({
    source: 'my-source'
});

// When the mouse leaves the `my-layer` layer,
// reset the entire state object for the
// feature under the mouse
map.on('mouseleave', 'my-layer', (e) => {
    map.removeFeatureState({
        source: 'my-source',
        sourceLayer: 'my-source-layer',
        id: e.features[0].id
    });
});

// When the mouse leaves the `my-layer` layer,
// reset only the `hover` key-value pair in the
// state for the feature under the mouse
map.on('mouseleave', 'my-layer', (e) => {
    map.removeFeatureState({
        source: 'my-source',
        sourceLayer: 'my-source-layer',
        id: e.features[0].id
    }, 'hover');
});

Gets the state of a feature. A feature's state is a set of user-defined key-value pairs that are assigned to a feature at runtime. Features are identified by their id attribute, which can be any number or string.

Note: To access the values in a feature's state object for the purposes of styling the feature, use the feature-state expression.
Parameters
Name	Description
feature
Object
	Feature identifier. Feature objects returned from Map#queryRenderedFeatures or event handlers can be used as feature identifiers.
feature.id
(number | string)
	Unique id of the feature. Can be an integer or a string, but supports string values only when the promoteId option has been applied to the source or the string can be cast to an integer.
feature.source
string
	The id of the vector or GeoJSON source for the feature.
feature.sourceLayer
string?
	(optional) For vector tile sources, sourceLayer is required .
Returns
Object: The state of the feature: a set of key-value pairs that was assigned to the feature at runtime.
Example

// When the mouse moves over the `my-layer` layer,
// get the feature state for the feature under the mouse
map.on('mousemove', 'my-layer', (e) => {
    if (e.features.length > 0) {
        map.getFeatureState({
            source: 'my-source',
            sourceLayer: 'my-source-layer',
            id: e.features[0].id
        });
    }
});

Lifecycle

Returns a Boolean indicating whether the map is in idle state:

    No camera transitions are in progress.
    All currently requested tiles have loaded.
    All fade/transition animations have completed.

Returns false if there are any camera or animation transitions in progress, if the style is not yet fully loaded, or if there has been a change to the sources or style that has not yet fully loaded.

If the map.repaint is set to true, the map will never be idle.
Returns
boolean: A Boolean indicating whether the map is idle.
Example

const isIdle = map.idle();

Returns a Boolean indicating whether the map is fully loaded.

Returns false if the style is not yet fully loaded, or if there has been a change to the sources or style that has not yet fully loaded.
Returns
boolean: A Boolean indicating whether the map is fully loaded.
Example

const isLoaded = map.loaded();

Returns a Boolean indicating whether the map is finished rendering, meaning all animations are finished.
Returns
boolean: A Boolean indicating whether map finished rendering.
Example

const frameReady = map.frameReady();

Clean up and release all internal resources associated with this map.

This includes DOM elements, event bindings, web workers, and WebGL resources.

Use this method when you are done using the map and wish to ensure that it no longer consumes browser resources. Afterwards, you must not call any other methods on the map.
Example

map.remove();

Trigger the rendering of a single frame. Use this method with custom layers to repaint the map when the layer's properties or properties associated with the layer's source change. Calling this multiple times before the next frame is rendered will still result in only a single frame being rendered.
Example

map.triggerRepaint();

Related

    Example: Add a 3D model
    Example: Add an animated icon to the map 

Debug features
Events
Search Events

Fired immediately after the map has been resized.
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// immediately after the map has been resized.
map.on('resize', () => {
    console.log('A resize event occurred.');
});

Fired after the last frame rendered before the map enters an "idle" state:

    No camera transitions are in progress
    All currently requested tiles have loaded
    All fade/transition animations have completed.

Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just before the map enters an "idle" state.
map.on('idle', () => {
    console.log('A idle event occurred.');
});

Fired immediately after the map has been removed with Map.event:remove.
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just after the map is removed.
map.on('remove', () => {
    console.log('A remove event occurred.');
});

Fired when a pointing device (usually a mouse) is pressed within the map.

Note: This event is compatible with the optional layerId parameter. If layerId is included as the second argument in Map#on, the event listener will fire only when the the cursor is pressed while inside a visible portion of the specifed layer.
Type
MapMouseEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener
map.on('mousedown', () => {
    console.log('A mousedown event has occurred.');
});

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener for a specific layer
map.on('mousedown', 'poi-label', () => {
    console.log('A mousedown event has occurred on a visible portion of the poi-label layer.');
});

Related

    Example: Highlight features within a bounding box
    Example: Create a draggable point 

Fired when a pointing device (usually a mouse) is released within the map.

Note: This event is compatible with the optional layerId parameter. If layerId is included as the second argument in Map#on, the event listener will fire only when the the cursor is released while inside a visible portion of the specifed layer.
Type
MapMouseEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener
map.on('mouseup', () => {
    console.log('A mouseup event has occurred.');
});

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener for a specific layer
map.on('mouseup', 'poi-label', () => {
    console.log('A mouseup event has occurred on a visible portion of the poi-label layer.');
});

Related

    Example: Highlight features within a bounding box
    Example: Create a draggable point 

Fired when a pointing device (usually a mouse) is moved within the map. As you move the cursor across a web page containing a map, the event will fire each time it enters the map or any child elements.

Note: This event is compatible with the optional layerId parameter. If layerId is included as the second argument in Map#on, the event listener will fire only when the the cursor is moved inside a visible portion of the specifed layer.
Type
MapMouseEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener
map.on('mouseover', () => {
    console.log('A mouseover event has occurred.');
});

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener for a specific layer
map.on('mouseover', 'poi-label', () => {
    console.log('A mouseover event has occurred on a visible portion of the poi-label layer.');
});

Related

    Example: Get coordinates of the mouse pointer
    Example: Highlight features under the mouse pointer
    Example: Display a popup on hover 

Fired when a pointing device (usually a mouse) is moved while the cursor is inside the map. As you move the cursor across the map, the event will fire every time the cursor changes position within the map.

Note: This event is compatible with the optional layerId parameter. If layerId is included as the second argument in Map#on, the event listener will fire only when the the cursor is inside a visible portion of the specified layer.
Type
MapMouseEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener
map.on('mousemove', () => {
    console.log('A mousemove event has occurred.');
});

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener for a specific layer
map.on('mousemove', 'poi-label', () => {
    console.log('A mousemove event has occurred on a visible portion of the poi-label layer.');
});

Related

    Example: Get coordinates of the mouse pointer
    Example: Highlight features under the mouse pointer
    Example: Display a popup on over 

Triggered when a click event occurs and is fired before the click event. Primarily implemented to ensure closeOnClick for pop-ups is fired before any other listeners.
Type
MapMouseEvent

Fired when a pointing device (usually a mouse) is pressed and released at the same point on the map.

Note: This event is compatible with the optional layerId parameter. If layerId is included as the second argument in Map#on, the event listener will fire only when the point that is pressed and released contains a visible portion of the specifed layer.
Type
MapMouseEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener
map.on('click', (e) => {
    console.log(`A click event has occurred at ${e.lngLat}`);
});

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener for a specific layer
map.on('click', 'poi-label', (e) => {
    console.log(`A click event has occurred on a visible portion of the poi-label layer at ${e.lngLat}`);
});

Related

    Example: Measure distances
    Example: Center the map on a clicked symbol 

Fired when a pointing device (usually a mouse) is pressed and released twice at the same point on the map in rapid succession.

Note: This event is compatible with the optional layerId parameter. If layerId is included as the second argument in Map#on, the event listener will fire only when the point that is clicked twice contains a visible portion of the specifed layer.
Type
MapMouseEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener
map.on('dblclick', (e) => {
    console.log(`A dblclick event has occurred at ${e.lngLat}`);
});

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener for a specific layer
map.on('dblclick', 'poi-label', (e) => {
    console.log(`A dblclick event has occurred on a visible portion of the poi-label layer at ${e.lngLat}`);
});

Fired when a pointing device (usually a mouse) enters a visible portion of a specified layer from outside that layer or outside the map canvas.

Important: This event can only be listened for when Map#on includes three arguments, where the second argument specifies the desired layer.
Type
MapMouseEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener
map.on('mouseenter', 'water', () => {
    console.log('A mouseenter event occurred on a visible portion of the water layer.');
});

Related

    Example: Center the map on a clicked symbol
    Example: Display a popup on click 

Fired when a pointing device (usually a mouse) leaves a visible portion of a specified layer or moves from the specified layer to outside the map canvas.

Note: To detect when the mouse leaves the canvas, independent of layer, use Map.event:mouseout instead.

Important: This event can only be listened for when Map#on includes three arguments, where the second argument specifies the desired layer.
Type
MapMouseEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the pointing device leaves
// a visible portion of the specified layer.
map.on('mouseleave', 'water', () => {
    console.log('A mouseleave event occurred.');
});

Related

    Example: Highlight features under the mouse pointer
    Example: Display a popup on click 

Fired when a point device (usually a mouse) leaves the map's canvas.
Type
MapMouseEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the pointing device leaves
// the map's canvas.
map.on('mouseout', () => {
    console.log('A mouseout event occurred.');
});

Fired when the right button of the mouse is clicked or the context menu key is pressed within the map.
Type
MapMouseEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the right mouse button is
// pressed within the map.
map.on('contextmenu', () => {
    console.log('A contextmenu event occurred.');
});

Fired when a wheel event occurs within the map.
Type
MapWheelEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when a wheel event occurs within the map.
map.on('wheel', () => {
    console.log('A wheel event occurred.');
});

Fired when a touchstart event occurs within the map.
Type
MapTouchEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when a `touchstart` event occurs within the map.
map.on('touchstart', () => {
    console.log('A touchstart event occurred.');
});

Related

    Example: Create a draggable point 

Fired when a touchend event occurs within the map.
Type
MapTouchEvent
Example

// Initialize the map.
const map = new mapboxgl.Map({});
// Set an event listener that fires when a `touchend` event occurs within the map.
map.on('touchend', () => {
    console.log('A touchend event occurred.');
});

Related

    Example: Create a draggable point 

Fired when a touchmove event occurs within the map.
Type
MapTouchEvent
Example

// Initialize the map.
const map = new mapboxgl.Map({});
// Set an event listener that fires when a touchmove event occurs within the map.
map.on('touchmove', () => {
    console.log('A touchmove event occurred.');
});

Related

    Example: Create a draggable point 

Fired when a touchcancel event occurs within the map.
Type
MapTouchEvent
Example

// Initialize the map.
const map = new mapboxgl.Map({});
// Set an event listener that fires when a `touchcancel` event occurs within the map.
map.on('touchcancel', () => {
    console.log('A touchcancel event occurred.');
});

Fired just before the map begins a transition from one view to another, as the result of either user interaction or methods such as Map#jumpTo.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map.
const map = new mapboxgl.Map({});
// Set an event listener that fires just before the map begins a transition from one view to another.
map.on('movestart', () => {
    console.log('A movestart` event occurred.');
});

Fired repeatedly during an animated transition from one view to another, as the result of either user interaction or methods such as Map#flyTo.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map.
const map = new mapboxgl.Map({});
// Set an event listener that fires repeatedly during an animated transition.
map.on('move', () => {
    console.log('A move event occurred.');
});

Related

    Example: Display HTML clusters with custom properties
    Example: Filter features within map view 

Fired just after the map completes a transition from one view to another, as the result of either user interaction or methods such as Map#jumpTo.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just after the map completes a transition.
map.on('moveend', () => {
    console.log('A moveend event occurred.');
});

Related

    Example: Play map locations as a slideshow
    Example: Filter features within map view
    Example: Display HTML clusters with custom properties 

Fired when a "drag to pan" interaction starts. See DragPanHandler.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when a "drag to pan" interaction starts.
map.on('dragstart', () => {
    console.log('A dragstart event occurred.');
});

Fired repeatedly during a "drag to pan" interaction. See DragPanHandler.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// repeatedly during a "drag to pan" interaction.
map.on('drag', () => {
    console.log('A drag event occurred.');
});

Fired when a "drag to pan" interaction ends. See DragPanHandler.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when a "drag to pan" interaction ends.
map.on('dragend', () => {
    console.log('A dragend event occurred.');
});

Related

    Example: Create a draggable marker 

Fired just before the map begins a transition from one zoom level to another, as the result of either user interaction or methods such as Map#flyTo.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just before a zoom transition starts.
map.on('zoomstart', () => {
    console.log('A zoomstart event occurred.');
});

Fired repeatedly during an animated transition from one zoom level to another, as the result of either user interaction or methods such as Map#flyTo.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// repeatedly during a zoom transition.
map.on('zoom', () => {
    console.log('A zoom event occurred.');
});

Related

    Example: Update a choropleth layer by zoom level 

Fired just after the map completes a transition from one zoom level to another as the result of either user interaction or methods such as Map#flyTo. The zoom transition will usually end before rendering is finished, so if you need to wait for rendering to finish, use the Map.event:idle event instead.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just after a zoom transition finishes.
map.on('zoomend', () => {
    console.log('A zoomend event occurred.');
});

Fired when a "drag to rotate" interaction starts. See DragRotateHandler.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just before a "drag to rotate" interaction starts.
map.on('rotatestart', () => {
    console.log('A rotatestart event occurred.');
});

Fired repeatedly during a "drag to rotate" interaction. See DragRotateHandler.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// repeatedly during "drag to rotate" interaction.
map.on('rotate', () => {
    console.log('A rotate event occurred.');
});

Fired when a "drag to rotate" interaction ends. See DragRotateHandler.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just after a "drag to rotate" interaction ends.
map.on('rotateend', () => {
    console.log('A rotateend event occurred.');
});

Fired whenever the map's pitch (tilt) begins a change as the result of either user interaction or methods such as Map#flyTo .
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just before a pitch (tilt) transition starts.
map.on('pitchstart', () => {
    console.log('A pitchstart event occurred.');
});

Fired repeatedly during the map's pitch (tilt) animation between one state and another as the result of either user interaction or methods such as Map#flyTo.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// repeatedly during a pitch (tilt) transition.
map.on('pitch', () => {
    console.log('A pitch event occurred.');
});

Fired immediately after the map's pitch (tilt) finishes changing as the result of either user interaction or methods such as Map#flyTo.
Type
(MapMouseEvent | MapTouchEvent)
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just after a pitch (tilt) transition ends.
map.on('pitchend', () => {
    console.log('A pitchend event occurred.');
});

Fired when a "box zoom" interaction starts. See BoxZoomHandler.
Type
MapBoxZoomEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just before a "box zoom" interaction starts.
map.on('boxzoomstart', () => {
    console.log('A boxzoomstart event occurred.');
});

Fired when a "box zoom" interaction ends. See BoxZoomHandler.
Type
MapBoxZoomEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// just after a "box zoom" interaction ends.
map.on('boxzoomend', () => {
    console.log('A boxzoomend event occurred.');
});

Fired when the user cancels a "box zoom" interaction, or when the bounding box does not meet the minimum size threshold. See BoxZoomHandler.
Type
MapBoxZoomEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// the user cancels a "box zoom" interaction.
map.on('boxzoomcancel', () => {
    console.log('A boxzoomcancel event occurred.');
});

Fired immediately after all necessary resources have been downloaded and the first visually complete rendering of the map has occurred.
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the map has finished loading.
map.on('load', () => {
    console.log('A load event occurred.');
});

Related

    Example: Draw GeoJSON points
    Example: Add live realtime data
    Example: Animate a point 

Fired whenever the rendering process of the map is started. This event can be used in pair with the "render" event, to measure the time spent on the CPU during the rendering of a single frame.
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the map begins rendering.
map.on('renderstart', () => {
    console.log('A renderstart event occurred.');
});

Fired whenever the map is drawn to the screen, as the result of:

    a change to the map's position, zoom, pitch, or bearing
    a change to the map's style
    a change to a GeoJSON source
    the loading of a vector tile, GeoJSON file, glyph, or sprite.

Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// whenever the map is drawn to the screen.
map.on('render', () => {
    console.log('A render event occurred.');
});

Fired when an error occurs. This is Mapbox GL JS's primary error reporting mechanism. We use an event instead of throw to better accommodate asyncronous operations. If no listeners are bound to the error event, the error will be printed to the console.
Properties
Name	Description
message
string
	Error message.
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when an error occurs.
map.on('error', () => {
    console.log('A error event occurred.');
});

Fired when the WebGL context is lost.
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the WebGL context is lost.
map.on('webglcontextlost', () => {
    console.log('A webglcontextlost event occurred.');
});

Fired when the WebGL context is restored.
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the WebGL context is restored.
map.on('webglcontextrestored', () => {
    console.log('A webglcontextrestored event occurred.');
});

Fired when any map data loads or changes. See MapDataEvent for more information.
Type
MapDataEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when map data loads or changes.
map.on('data', () => {
    console.log('A data event occurred.');
});

Related

    Example: Display HTML clusters with custom properties 

Fired when the map's style loads or changes. See MapDataEvent for more information.
Type
MapDataEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the map's style loads or changes.
map.on('styledata', () => {
    console.log('A styledata event occurred.');
});

Fired when one of the map's sources loads or changes, including if a tile belonging to a source loads or changes. See MapDataEvent for more information.
Type
MapDataEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when one of the map's sources loads or changes.
map.on('sourcedata', () => {
    console.log('A sourcedata event occurred.');
});

Fired when any map data (style, source, tile, etc) begins loading or changing asynchronously. All dataloading events are followed by a data or error event. See MapDataEvent for more information.
Type
MapDataEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when any map data begins loading
// or changing asynchronously.
map.on('dataloading', () => {
    console.log('A dataloading event occurred.');
});

Fired when the map's style begins loading or changing asynchronously. All styledataloading events are followed by a styledata or error event. See MapDataEvent for more information.
Type
MapDataEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the map's style begins loading or
// changing asynchronously.
map.on('styledataloading', () => {
    console.log('A styledataloading event occurred.');
});

Fired when one of the map's sources begins loading or changing asynchronously. All sourcedataloading events are followed by a sourcedata or error event. See MapDataEvent for more information.
Type
MapDataEvent
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the map's sources begin loading or
// changing asynchronously.
map.on('sourcedataloading', () => {
    console.log('A sourcedataloading event occurred.');
});

Fired when an icon or pattern needed by the style is missing. The missing image can be added with Map#addImage within this event listener callback to prevent the image from being skipped. This event can be used to dynamically generate icons and patterns.
Properties
Name	Description
id
string
	The id of the missing image.
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when an icon or pattern is missing.
map.on('styleimagemissing', () => {
    console.log('A styleimagemissing event occurred.');
});

Related

    Example: Generate and add a missing icon to the map 

Fired immediately after all style resources have been downloaded and the first visually complete rendering of the base style has occurred.

In general, it's recommended to add custom sources and layers after this event. This approach allows for a more efficient initialization and faster rendering of the added layers.
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the map has finished loading.
map.on('style.load', () => {
    console.log('A style load event occurred.');
});

Related

    Example: Persist layers when switching base style 

Fired immediately after imported style resources have been downloaded and the first visually complete rendering of the base style extended with the imported style has occurred.
Example

// Initialize the map
const map = new mapboxgl.Map({});
// Set an event listener that fires
// when the style import has finished loading.
map.on('style.import.load', () => {
    console.log('A style import load event occurred.');
});

Related

    Example: Display a map on a webpage
    Example: Display a map with a custom style
    Example: Check if Mapbox GL JS is supported 

Was this page helpful?
Was this page helpful?
© Mapbox All Rights Reserved
Terms
Privacy
Security
Your California Privacy Choices
Skip to main content
Docs

English

Mapbox GL JS

    Guides

API Reference

        Map
        Properties and options
        Markers and controls
        User interaction handlers
        Sources
        Events and event types
        Geography and geometry
    Plugins and frameworks
    Examples
    Style Specificationshare
    Tutorialsshare
    Troubleshootingshare

    All docschevron-rightMapbox GL JSchevron-rightAPI Referencechevron-rightGeography and geometry

Geography and geometry
Search GL JS API Reference
On this page

    LngLat
        Parameters
        Example
        Static members
        Instance members
        Related
    LngLatBounds
        Parameters
        Example
        Static members
        Instance members
    LngLatBoundsLike
        Example
    LngLatLike
        Example
    MercatorCoordinate
        Parameters
        Example
        Static members
        Instance members
        Related
    Point
        Example
    PointLike
        Example

General utilities and types that relate to working with and manipulating geographic information or geometries.
LngLat
githubsrc/geo/lng_lat.ts

A LngLat object represents a given longitude and latitude coordinate, measured in degrees. These coordinates use longitude, latitude coordinate order (as opposed to latitude, longitude) to match the GeoJSON specification, which is equivalent to the OGC:CRS84 coordinate reference system.

Note that any Mapbox GL method that accepts a LngLat object as an argument or option can also accept an Array of two numbers and will perform an implicit conversion. This flexible type is documented as LngLatLike.
new LngLat(lng: number, lat: number)
Parameters
Name	Description
lng
number
	Longitude, measured in degrees.
lat
number
	Latitude, measured in degrees.
Example

const ll = new mapboxgl.LngLat(-123.9749, 40.7736);
console.log(ll.lng); // = -123.9749

Static Members

Converts an array of two numbers or an object with lng and lat or lon and lat properties to a LngLat object.

If a LngLat object is passed in, the function returns it unchanged.
Parameters
Name	Description
input
LngLatLike
	An array of two numbers or object to convert, or a LngLat object to return.
Returns
LngLat: A new LngLat object, if a conversion occurred, or the original LngLat object.
Example

const arr = [-73.9749, 40.7736];
const ll = mapboxgl.LngLat.convert(arr);
console.log(ll);   // = LngLat {lng: -73.9749, lat: 40.7736}

Instance Members

Returns a new LngLat object whose longitude is wrapped to the range (-180, 180).
Returns
LngLat: The wrapped LngLat object.
Example

const ll = new mapboxgl.LngLat(286.0251, 40.7736);
const wrapped = ll.wrap();
console.log(wrapped.lng); // = -73.9749

Returns the coordinates represented as an array of two numbers.
Returns
Array<number>: The coordinates represeted as an array of longitude and latitude.
Example

const ll = new mapboxgl.LngLat(-73.9749, 40.7736);
ll.toArray(); // = [-73.9749, 40.7736]

Returns the coordinates represent as a string.
Returns
string: The coordinates represented as a string of the format 'LngLat(lng, lat)' .
Example

const ll = new mapboxgl.LngLat(-73.9749, 40.7736);
ll.toString(); // = "LngLat(-73.9749, 40.7736)"

Returns the approximate distance between a pair of coordinates in meters. Uses the Haversine Formula (from R.W. Sinnott, "Virtues of the Haversine", Sky and Telescope, vol. 68, no. 2, 1984, p. 159).
Parameters
Name	Description
lngLat
LngLat
	Coordinates to compute the distance to.
Returns
number: Distance in meters between the two coordinates.
Example

const newYork = new mapboxgl.LngLat(-74.0060, 40.7128);
const losAngeles = new mapboxgl.LngLat(-118.2437, 34.0522);
newYork.distanceTo(losAngeles); // = 3935751.690893987, "true distance" using a non-spherical approximation is ~3966km

Returns a LngLatBounds from the coordinates extended by a given radius. The returned LngLatBounds completely contains the radius.
Parameters
Name	Description
radius
number
(default 0)
	Distance in meters from the coordinates to extend the bounds.
Returns
LngLatBounds: A new LngLatBounds object representing the coordinates extended by the radius .
Example

const ll = new mapboxgl.LngLat(-73.9749, 40.7736);
ll.toBounds(100).toArray(); // = [[-73.97501862141328, 40.77351016847229], [-73.97478137858673, 40.77368983152771]]

Related

    Example: Get coordinates of the mouse pointer
    Example: Display a popup
    Example: Highlight features within a bounding box
    Example: Create a timeline animation 

Was this section on LngLat helpful?
LngLatBounds
githubsrc/geo/lng_lat.ts

A LngLatBounds object represents a geographical bounding box, defined by its southwest and northeast points in longitude and latitude. Longitude values are typically set between -180 to 180, but can exceed this range if renderWorldCopies is set to true. Latitude values must be within -85.051129 to 85.051129.

If no arguments are provided to the constructor, a null bounding box is created.

Note that any Mapbox GL method that accepts a LngLatBounds object as an argument or option can also accept an Array of two LngLatLike constructs and will perform an implicit conversion. This flexible type is documented as LngLatBoundsLike.
new LngLatBounds(sw: LngLatLike?, ne: LngLatLike?)
Parameters
Name	Description
sw
LngLatLike?
	The southwest corner of the bounding box.
ne
LngLatLike?
	The northeast corner of the bounding box.
Example

const sw = new mapboxgl.LngLat(-73.9876, 40.7661);
const ne = new mapboxgl.LngLat(-73.9397, 40.8002);
const llb = new mapboxgl.LngLatBounds(sw, ne);

Static Members

Converts an array to a LngLatBounds object.

If a LngLatBounds object is passed in, the function returns it unchanged.

Internally, the function calls LngLat#convert to convert arrays to LngLat values.
Parameters
Name	Description
input
LngLatBoundsLike
	An array of two coordinates to convert, or a LngLatBounds object to return.
Returns
(LngLatBounds | void): A new LngLatBounds object, if a conversion occurred, or the original LngLatBounds object.
Example

const arr = [[-73.9876, 40.7661], [-73.9397, 40.8002]];
const llb = mapboxgl.LngLatBounds.convert(arr);
console.log(llb);   // = LngLatBounds {_sw: LngLat {lng: -73.9876, lat: 40.7661}, _ne: LngLat {lng: -73.9397, lat: 40.8002}}

Instance Members
Search Instance Members

Set the northeast corner of the bounding box.
Parameters
Name	Description
ne
LngLatLike
	A LngLatLike object describing the northeast corner of the bounding box.
Returns
LngLatBounds: Returns itself to allow for method chaining.
Example

const sw = new mapboxgl.LngLat(-73.9876, 40.7661);
const ne = new mapboxgl.LngLat(-73.9397, 40.8002);
const llb = new mapboxgl.LngLatBounds(sw, ne);
llb.setNorthEast([-73.9397, 42.8002]);

Set the southwest corner of the bounding box.
Parameters
Name	Description
sw
LngLatLike
	A LngLatLike object describing the southwest corner of the bounding box.
Returns
LngLatBounds: Returns itself to allow for method chaining.
Example

const sw = new mapboxgl.LngLat(-73.9876, 40.7661);
const ne = new mapboxgl.LngLat(-73.9397, 40.8002);
const llb = new mapboxgl.LngLatBounds(sw, ne);
llb.setSouthWest([-73.9876, 40.2661]);

Extend the bounds to include a given LngLatLike or LngLatBoundsLike.
Parameters
Name	Description
obj
(LngLatLike | LngLatBoundsLike)
	Object to extend to.
Returns
LngLatBounds: Returns itself to allow for method chaining.
Example

const sw = new mapboxgl.LngLat(-73.9876, 40.7661);
const ne = new mapboxgl.LngLat(-73.9397, 40.8002);
const llb = new mapboxgl.LngLatBounds(sw, ne);
llb.extend([-72.9876, 42.2661]);

Returns the geographical coordinate equidistant from the bounding box's corners.
Returns
LngLat: The bounding box's center.
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.getCenter(); // = LngLat {lng: -73.96365, lat: 40.78315}

Returns the southwest corner of the bounding box.
Returns
LngLat: The southwest corner of the bounding box.
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.getSouthWest(); // LngLat {lng: -73.9876, lat: 40.7661}

Returns the northeast corner of the bounding box.
Returns
LngLat: The northeast corner of the bounding box.
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.getNorthEast(); // LngLat {lng: -73.9397, lat: 40.8002}

Returns the northwest corner of the bounding box.
Returns
LngLat: The northwest corner of the bounding box.
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.getNorthWest(); // LngLat {lng: -73.9876, lat: 40.8002}

Returns the southeast corner of the bounding box.
Returns
LngLat: The southeast corner of the bounding box.
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.getSouthEast(); // LngLat {lng: -73.9397, lat: 40.7661}

Returns the west edge of the bounding box.
Returns
number: The west edge of the bounding box.
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.getWest(); // -73.9876

Returns the south edge of the bounding box.
Returns
number: The south edge of the bounding box.
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.getSouth(); // 40.7661

Returns the east edge of the bounding box.
Returns
number: The east edge of the bounding box.
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.getEast(); // -73.9397

Returns the north edge of the bounding box.
Returns
number: The north edge of the bounding box.
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.getNorth(); // 40.8002

Returns the bounding box represented as an array.
Returns
Array<Array<number>>: The bounding box represented as an array, consisting of the southwest and northeast coordinates of the bounding represented as arrays of numbers.
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.toArray(); // = [[-73.9876, 40.7661], [-73.9397, 40.8002]]

Return the bounding box represented as a string.
Returns
string: The bounding box represents as a string of the format 'LngLatBounds(LngLat(lng, lat), LngLat(lng, lat))' .
Example

const llb = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
llb.toString(); // = "LngLatBounds(LngLat(-73.9876, 40.7661), LngLat(-73.9397, 40.8002))"

Check if the bounding box is an empty/null-type box.
Returns
boolean: True if bounds have been defined, otherwise false.
Example

const llb = new mapboxgl.LngLatBounds();
llb.isEmpty(); // true
llb.setNorthEast([-73.9876, 40.7661]);
llb.setSouthWest([-73.9397, 40.8002]);
llb.isEmpty(); // false

Check if the point is within the bounding box.
Parameters
Name	Description
lnglat
LngLatLike
	Geographic point to check against.
Returns
boolean: True if the point is within the bounding box.
Example

const llb = new mapboxgl.LngLatBounds(
  new mapboxgl.LngLat(-73.9876, 40.7661),
  new mapboxgl.LngLat(-73.9397, 40.8002)
);

const ll = new mapboxgl.LngLat(-73.9567, 40.7789);

console.log(llb.contains(ll)); // = true

Was this section on LngLatBounds helpful?
LngLatBoundsLike
githubsrc/geo/lng_lat.ts

A LngLatBounds object, an array of LngLatLike objects in [sw, ne] order, or an array of numbers in [west, south, east, north] order.
Type
(LngLatBounds | [LngLatLike, LngLatLike] | [number, number, number, number])
Example

const v1 = new mapboxgl.LngLatBounds(
  new mapboxgl.LngLat(-73.9876, 40.7661),
  new mapboxgl.LngLat(-73.9397, 40.8002)
);
const v2 = new mapboxgl.LngLatBounds([-73.9876, 40.7661], [-73.9397, 40.8002]);
const v3 = [[-73.9876, 40.7661], [-73.9397, 40.8002]];

Was this section on LngLatBoundsLike helpful?
LngLatLike
githubsrc/geo/lng_lat.ts

A LngLat object, an array of two numbers representing longitude and latitude, or an object with lng and lat or lon and lat properties.
Type
(LngLat | {lng: number, lat: number} | {lon: number, lat: number} | [number, number])
Example

const v1 = new mapboxgl.LngLat(-122.420679, 37.772537);
const v2 = [-122.420679, 37.772537];
const v3 = {lon: -122.420679, lat: 37.772537};

Was this section on LngLatLike helpful?
MercatorCoordinate
githubsrc/geo/mercator_coordinate.ts

A MercatorCoordinate object represents a projected three dimensional position.

MercatorCoordinate uses the web mercator projection (EPSG:3857) with slightly different units:

    the size of 1 unit is the width of the projected world instead of the "mercator meter"
    the origin of the coordinate space is at the north-west corner instead of the middle.

For example, MercatorCoordinate(0, 0, 0) is the north-west corner of the mercator world and MercatorCoordinate(1, 1, 0) is the south-east corner. If you are familiar with vector tiles it may be helpful to think of the coordinate space as the 0/0/0 tile with an extent of 1.

The z dimension of MercatorCoordinate is conformal. A cube in the mercator coordinate space would be rendered as a cube.
new MercatorCoordinate(x: number, y: number, z: number)
Parameters
Name	Description
x
number
	The x component of the position.
y
number
	The y component of the position.
z
number
(default 0)
	The z component of the position.
Example

const nullIsland = new mapboxgl.MercatorCoordinate(0.5, 0.5, 0);

Static Members

Project a LngLat to a MercatorCoordinate.
Parameters
Name	Description
lngLatLike
LngLatLike
	The location to project.
altitude
number
(default 0)
	The altitude in meters of the position.
Returns
MercatorCoordinate: The projected mercator coordinate.
Example

const coord = mapboxgl.MercatorCoordinate.fromLngLat({lng: 0, lat: 0}, 0);
console.log(coord); // MercatorCoordinate(0.5, 0.5, 0)

Instance Members

Returns the LngLat for the coordinate.
Returns
LngLat: The LngLat object.
Example

const coord = new mapboxgl.MercatorCoordinate(0.5, 0.5, 0);
const lngLat = coord.toLngLat(); // LngLat(0, 0)

Returns the altitude in meters of the coordinate.
Returns
number: The altitude in meters.
Example

const coord = new mapboxgl.MercatorCoordinate(0, 0, 0.02);
coord.toAltitude(); // 6914.281956295339

Returns the distance of 1 meter in MercatorCoordinate units at this latitude.

For coordinates in real world units using meters, this naturally provides the scale to transform into MercatorCoordinates.
Returns
number: Distance of 1 meter in MercatorCoordinate units.
Example

// Calculate a new MercatorCoordinate that is 150 meters west of the other coord.
const coord = new mapboxgl.MercatorCoordinate(0.5, 0.25, 0);
const offsetInMeters = 150;
const offsetInMercatorCoordinateUnits = offsetInMeters * coord.meterInMercatorCoordinateUnits();
const westCoord = new mapboxgl.MercatorCoordinate(coord.x - offsetInMercatorCoordinateUnits, coord.y, coord.z);

Related

    Example: Add a custom style layer 

Was this section on MercatorCoordinate helpful?
Point
githubsrc/ui/map.ts

A Point geometry object, which has x and y screen coordinates in pixels, or other units.
Type
Point
Example

const point = new mapboxgl.Point(400, 525);

Was this section on Point helpful?
PointLike
githubsrc/ui/map.ts

A Point or an array of two numbers representing x and y screen coordinates in pixels, or other units.
Type
(Point | Array<number>)
Example

const p1 = new mapboxgl.Point(400, 525); // a PointLike which is a Point
const p2 = [400, 525]; // a PointLike which is an array of two numbers

Was this section on PointLike helpful?
Was this page helpful?
© Mapbox All Rights Reserved
Terms
Privacy
Security
Your California Privacy Choices
Skip to main content
Docs

English

Mapbox GL JS

    Guides

API Reference

        Map
        Properties and options
        Markers and controls
        User interaction handlers
        Sources
        Events and event types
        Geography and geometry
    Plugins and frameworks
    Examples
    Style Specificationshare
    Tutorialsshare
    Troubleshootingshare

    All docschevron-rightMapbox GL JSchevron-rightAPI Referencechevron-rightEvents and event types

Events and event types
Search GL JS API Reference
On this page

    Evented
        Instance members
    MapBoxZoomEvent
        Properties
        Example
        Related
    MapDataEvent
        Properties
        Example
        Related
    MapMouseEvent
        Example
        Instance members
        Related
    MapTouchEvent
        Example
        Instance members
        Related
    MapWheelEvent
        Example
        Instance members
        Related

Map and other Mapbox GL JS classes emit events in response to user interactions or changes in state. Evented is the interface used to bind and unbind listeners for these events. This page describes the different types of events that Mapbox GL JS can raise.

You can learn more about the originating events here:

    Map events fire when a user interacts with a Map.
    Marker events fire when a user interacts with a Marker.
    Popup events fire when a user interacts with a Popup.
    GeolocationControl events fire when a user interacts with a GeolocationControl.

Evented
githubsrc/util/evented.ts

Evented mixes methods into other classes for event capabilities.

Unless you are developing a plugin you will most likely use these methods through classes like Map or Popup.

For lists of events you can listen for, see API documentation for specific classes: Map, Marker, Popup, and GeolocationControl.
Instance Members

Adds a listener to a specified event type.
Parameters
Name	Description
type
string
	The event type to add a listen for.
listener
Function
	The function to be called when the event is fired. The listener function is called with the data object passed to fire , extended with target and type properties.
Returns
Object: Returns itself to allow for method chaining.

Removes a previously registered event listener.
Parameters
Name	Description
type
string
	The event type to remove listeners for.
listener
Function
	The listener function to remove.
Returns
Object: Returns itself to allow for method chaining.

Adds a listener that will be called only once to a specified event type.

The listener will be called first time the event fires after the listener is registered.
Parameters
Name	Description
type
string
	The event type to listen for.
listener
Function
	(Optional) The function to be called when the event is fired once. If not provided, returns a Promise that will be resolved when the event is fired once.
Returns
Object: Returns this | Promise.
Was this section on Evented helpful?
MapBoxZoomEvent
githubsrc/ui/events.ts

MapBoxZoomEvent is a class used to generate the events 'boxzoomstart', 'boxzoomend', and 'boxzoomcancel'. For a full list of available events, see Map events.
Type
Object
Properties
Name	Description
originalEvent
MouseEvent
	The DOM event that triggered the boxzoom event. Can be a MouseEvent or KeyboardEvent .
target
Map
	The Map instance that triggered the event.
type
("boxzoomstart" | "boxzoomend" | "boxzoomcancel")
	The type of originating event. For a full list of available events, see Map events .
Example

// Example trigger of a BoxZoomEvent of type "boxzoomstart"
map.on('boxzoomstart', (e) => {
    console.log('event type:', e.type);
    // event type: boxzoomstart
});

// Example of a BoxZoomEvent of type "boxzoomstart"
// {
//   originalEvent: {...},
//   type: "boxzoomstart",
//   target: {...}
// }

Related

    Reference: Map events API documentation
    Example: Highlight features within a bounding box 

Was this section on MapBoxZoomEvent helpful?
MapDataEvent
githubsrc/ui/events.ts

MapDataEvent is a type of events related to loading data, styles, and sources. For a full list of available events, see Map events.
Type
Object
Properties
Name	Description
coord
OverscaledTileID?
	The coordinate of the tile if the event has a dataType of source and the event is related to loading of a tile.
dataType
("source" | "style")
	The type of data that has changed. One of 'source' or 'style' , where 'source' refers to the data associated with any source, and 'style' refers to the entire style used by the map.
isSourceLoaded
boolean?
	True if the event has a dataType of source and the source has no outstanding network requests.
source
Object?
	The style spec representation of the source if the event has a dataType of source .
sourceDataType
string?
	Included if the event has a dataType of source and the event signals that internal data has been received or changed. Possible values are metadata , content and visibility , and error .
sourceId
string?
	The id of the source that triggered the event, if the event has a dataType of source . Same as the id of the object in the source property.
tile
Object?
	The tile being loaded or changed, if the event has a dataType of source and the event is related to loading of a tile.
type
("data" | "dataloading" | "styledata" | "styledataloading" | "sourcedata" | "sourcedataloading")
	The type of originating event. For a full list of available events, see Map events .
Example

// Example of a MapDataEvent of type "sourcedata"
map.on('sourcedata', (e) => {
    console.log(e);
    // {
    //   dataType: "source",
    //   isSourceLoaded: false,
    //   source: {
    //     type: "vector",
    //     url: "mapbox://mapbox.mapbox-streets-v8,mapbox.mapbox-terrain-v2"
    //   },
    //   sourceDataType: "visibility",
    //   sourceId: "composite",
    //   style: {...},
    //   target: {...},
    //   type: "sourcedata"
    // }
});

Related

    Reference: Map events API documentation
    Example: Change a map's style
    Example: Add a GeoJSON line 

Was this section on MapDataEvent helpful?
MapMouseEvent
githubsrc/ui/events.ts

MapMouseEvent is a class used by other classes to generate mouse events of specific types such as 'click' or 'hover'. For a full list of available events, see Map events.
Extends Object.
Example

// Example of a MapMouseEvent of type "click"
map.on('click', (e) => {
    console.log(e);
    // {
    //     lngLat: {
    //         lng: 40.203,
    //         lat: -74.451
    //     },
    //     originalEvent: {...},
    //     point: {
    //         x: 266,
    //         y: 464
    //     },
    //      target: {...},
    //      type: "click"
    // }
});

Instance Members

The type of originating event. For a full list of available events, see Map events.
Type
MapMouseEventType

The Map object that fired the event.
Type
MapboxMap

The DOM event which caused the map event.
Type
MouseEvent

The pixel coordinates of the mouse cursor, relative to the map and measured from the top left corner.
Type
Point

The geographic location on the map of the mouse cursor.
Type
LngLat

If a single layerId(as a single string) or multiple layerIds (as an array of strings) were specified when adding the event listener with Map#on, features will be an array of GeoJSON Feature objects. The array will contain all features from that layer that are rendered at the event's point, in the order that they are rendered with the topmost feature being at the start of the array. The features are identical to those returned by Map#queryRenderedFeatures.

If no layerId was specified when adding the event listener, features will be undefined. You can get the features at the point with map.queryRenderedFeatures(e.point).
Type
Array<GeoJSONFeature>
Example

// logging features for a specific layer (with `e.features`)
map.on('click', 'myLayerId', (e) => {
    console.log(`There are ${e.features.length} features at point ${e.point}`);
});

// logging features for two layers (with `e.features`)
map.on('click', ['layer1', 'layer2'], (e) => {
    console.log(`There are ${e.features.length} features at point ${e.point}`);
});

// logging all features for all layers (without `e.features`)
map.on('click', (e) => {
    const features = map.queryRenderedFeatures(e.point);
    console.log(`There are ${features.length} features at point ${e.point}`);
});

Prevents subsequent default processing of the event by the map.

Calling this method will prevent the following default map behaviors:

    On mousedown events, the behavior of DragPanHandler.
    On mousedown events, the behavior of DragRotateHandler.
    On mousedown events, the behavior of BoxZoomHandler.
    On dblclick events, the behavior of DoubleClickZoomHandler.

Example

map.on('click', (e) => {
    e.preventDefault();
});

Related

    Reference: Map events API documentation
    Example: Display popup on click
    Example: Display popup on hover 

Was this section on MapMouseEvent helpful?
MapTouchEvent
githubsrc/ui/events.ts

MapTouchEvent is a class used by other classes to generate mouse events of specific types such as 'touchstart' or 'touchend'. For a full list of available events, see Map events.
Extends Object.
Example

// Example of a MapTouchEvent of type "touch"
map.on('touchstart', (e) => {
    console.log(e);
    // {
    //   lngLat: {
    //      lng: 40.203,
    //      lat: -74.451
    //   },
    //   lngLats: [
    //      {
    //         lng: 40.203,
    //         lat: -74.451
    //      }
    //   ],
    //   originalEvent: {...},
    //   point: {
    //      x: 266,
    //      y: 464
    //   },
    //   points: [
    //      {
    //         x: 266,
    //         y: 464
    //      }
    //   ]
    //   preventDefault(),
    //   target: {...},
    //   type: "touchstart"
    // }
});

Instance Members

The type of originating event. For a full list of available events, see Map events.
Type
MapTouchEventType

The Map object that fired the event.
Type
MapboxMap

The DOM event which caused the map event.
Type
TouchEvent

The geographic location on the map of the center of the touch event points.
Type
LngLat

The pixel coordinates of the center of the touch event points, relative to the map and measured from the top left corner.
Type
Point

The array of pixel coordinates corresponding to a touch event's touches property.
Type
Array<Point>

The geographical locations on the map corresponding to a touch event's touches property.
Type
Array<LngLat>

If a layerId was specified when adding the event listener with Map#on, features will be an array of GeoJSON Feature objects. The array will contain all features from that layer that are rendered at the event's point. The features are identical to those returned by Map#queryRenderedFeatures.

If no layerId was specified when adding the event listener, features will be undefined. You can get the features at the point with map.queryRenderedFeatures(e.point).
Type
(Array<GeoJSONFeature> | undefined)
Example

// logging features for a specific layer (with `e.features`)
map.on('touchstart', 'myLayerId', (e) => {
    console.log(`There are ${e.features.length} features at point ${e.point}`);
});

// logging all features for all layers (without `e.features`)
map.on('touchstart', (e) => {
    const features = map.queryRenderedFeatures(e.point);
    console.log(`There are ${features.length} features at point ${e.point}`);
});

Prevents subsequent default processing of the event by the map.

Calling this method will prevent the following default map behaviors:

    On touchstart events, the behavior of DragPanHandler.
    On touchstart events, the behavior of TouchZoomRotateHandler.

Example

map.on('touchstart', (e) => {
    e.preventDefault();
});

Related

    Reference: Map events API documentation
    Example: Create a draggable point 

Was this section on MapTouchEvent helpful?
MapWheelEvent
githubsrc/ui/events.ts

MapWheelEvent is a class used by other classes to generate mouse events of specific types such as 'wheel'. For a full list of available events, see Map events.
Extends Object.
Example

// Example event trigger for a MapWheelEvent of type "wheel"
map.on('wheel', (e) => {
    console.log('event type:', e.type);
    // event type: wheel
});

// Example of a MapWheelEvent of type "wheel"
// {
//   originalEvent: WheelEvent {...},
// 	 target: Map {...},
// 	 type: "wheel"
// }

Instance Members

The type of originating event. For a full list of available events, see Map events.
Type
MapWheelEventType

The Map object that fired the event.
Type
MapboxMap

The DOM event which caused the map event.
Type
WheelEvent

Prevents subsequent default processing of the event by the map. Calling this method will prevent the the behavior of ScrollZoomHandler.
Example

map.on('wheel', (e) => {
    // Prevent the default map scroll zoom behavior.
    e.preventDefault();
});

Related

    Reference: Map events API documentation 

Was this section on MapWheelEvent helpful?
Was this page helpful?
© Mapbox All Rights Reserved
Terms
Privacy
Security
Your California Privacy Choices

Skip to main content
Docs

English

Mapbox GL JS

    Guides

API Reference

        Map
        Properties and options
        Markers and controls
        User interaction handlers
        Sources
        Events and event types
        Geography and geometry
    Plugins and frameworks
    Examples
    Style Specificationshare
    Tutorialsshare
    Troubleshootingshare

    All docschevron-rightMapbox GL JSchevron-rightAPI Referencechevron-rightSources

Sources
Search GL JS API Reference
On this page

    CanvasSource
        Example
        Instance members
        Related
    CanvasSourceOptions
        Properties
    GeoJSONSource
        Example
        Instance members
        Related
    ImageSource
        Example
        Instance members
        Related
    ModelSource
        Example
        Instance members
    RasterArrayTileSource
        Parameters
        Example
        Instance members
        Related
    RasterTileSource
        Parameters
        Example
        Instance members
        Related
    VectorTileSource
        Parameters
        Example
        Instance members
        Related
    VideoSource
        Example
        Instance members
        Related

A source defines data the map should display. This reference lists the source types Mapbox GL JS can handle in addition to the ones described in the Mapbox Style Specification.
CanvasSource
githubsrc/source/canvas_source.ts

A data source containing the contents of an HTML canvas. See CanvasSourceOptions for detailed documentation of options.
Extends ImageSource.
Example

// add to map
map.addSource('some id', {
    type: 'canvas',
    canvas: 'idOfMyHTMLCanvas',
    animate: true,
    coordinates: [
        [-76.54, 39.18],
        [-76.52, 39.18],
        [-76.52, 39.17],
        [-76.54, 39.17]
    ]
});

// update
const mySource = map.getSource('some id');
mySource.setCoordinates([
    [-76.54335737228394, 39.18579907229748],
    [-76.52803659439087, 39.1838364847587],
    [-76.5295386314392, 39.17683392507606],
    [-76.54520273208618, 39.17876344106642]
]);

map.removeSource('some id');  // remove

Instance Members

Enables animation. The image will be copied from the canvas to the map on each frame.

Disables animation. The map will display a static copy of the canvas image.

Returns the HTML canvas element.
Returns
HTMLCanvasElement: The HTML canvas element.
Example

// Assuming the following canvas is added to your page
// <canvas id="canvasID" width="400" height="400"></canvas>
map.addSource('canvas-source', {
    type: 'canvas',
    canvas: 'canvasID',
    coordinates: [
        [91.4461, 21.5006],
        [100.3541, 21.5006],
        [100.3541, 13.9706],
        [91.4461, 13.9706]
    ]
});
map.getSource('canvas-source').getCanvas(); // <canvas id="canvasID" width="400" height="400"></canvas>

Sets the canvas's coordinates and re-renders the map.
Parameters
Name	Description
coordinates
Array<Array<number>>
	Four geographical coordinates, represented as arrays of longitude and latitude numbers, which define the corners of the canvas. The coordinates start at the top left corner of the canvas and proceed in clockwise order. They do not have to represent a rectangle.
Returns
CanvasSource: Returns itself to allow for method chaining.
Related

    Example: Add a canvas source 

Was this section on CanvasSource helpful?
CanvasSourceOptions
githubsrc/source/canvas_source.ts

Options to add a canvas source type to the map.
Type
Object
Properties
Name	Description
animate
boolean?
	Whether the canvas source is animated. If the canvas is static (pixels do not need to be re-read on every frame), animate should be set to false to improve performance.
canvas
(string | HTMLCanvasElement)
	Canvas source from which to read pixels. Can be a string representing the ID of the canvas element, or the HTMLCanvasElement itself.
coordinates
Array<Array<number>>
	Four geographical coordinates denoting where to place the corners of the canvas, specified in [longitude, latitude] pairs.
type
string
	Source type. Must be "canvas" .
Was this section on CanvasSourceOptions helpful?
GeoJSONSource
githubsrc/source/geojson_source.ts

A source containing GeoJSON. See the Style Specification for detailed documentation of options.
Extends Evented.
Example

map.addSource('some id', {
    type: 'geojson',
    data: 'https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_10m_ports.geojson'
});

map.addSource('some id', {
    type: 'geojson',
    data: {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Point",
                "coordinates": [
                    -76.53063297271729,
                    39.18174077994108
                ]
            }
        }]
    }
});

map.getSource('some id').setData({
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {"name": "Null Island"},
        "geometry": {
            "type": "Point",
            "coordinates": [ 0, 0 ]
        }
    }]
});

Instance Members

Sets the GeoJSON data and re-renders the map.
Parameters
Name	Description
data
(Object | string)
	A GeoJSON data object or a URL to one. The latter is preferable in the case of large GeoJSON files.
Returns
GeoJSONSource: Returns itself to allow for method chaining.
Example

map.addSource('source_id', {
    type: 'geojson',
    data: {
        type: 'FeatureCollection',
        features: []
    }
});
const geojsonSource = map.getSource('source_id');
// Update the data after the GeoJSON source was created
geojsonSource.setData({
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {"name": "Null Island"},
        "geometry": {
            "type": "Point",
            "coordinates": [ 0, 0 ]
        }
    }]
});

Updates the existing GeoJSON data with new features and re-renders the map. Can only be used on sources with dynamic: true in options. Updates features by their IDs:

    If there's a feature with the same ID, overwrite it.
    If there's a feature with the same ID but the new one's geometry is null, remove it
    If there's no such ID in existing data, add it as a new feature.

Parameters
Name	Description
data
(Object | string)
	A GeoJSON data object or a URL to one.
Returns
GeoJSONSource: Returns itself to allow for method chaining.
Example

// Update the feature with ID=123 in the existing GeoJSON source
map.getSource('source_id').updateData({
    "type": "FeatureCollection",
    "features": [{
        "id": 123,
        "type": "Feature",
        "properties": {"name": "Null Island"},
        "geometry": {
            "type": "Point",
            "coordinates": [ 0, 0 ]
        }
    }]
});

For clustered sources, fetches the zoom at which the given cluster expands.
Parameters
Name	Description
clusterId
number
	The value of the cluster's cluster_id property.
callback
Function
	A callback to be called when the zoom value is retrieved ( (error, zoom) => { ... } ).
Returns
GeoJSONSource: Returns itself to allow for method chaining.
Example

// Assuming the map has a layer named 'clusters' and a source 'earthquakes'
// The following creates a camera animation on cluster feature click
// the clicked layer should be filtered to only include clusters, e.g. `filter: ['has', 'point_count']`
map.on('click', 'clusters', (e) => {
    const features = map.queryRenderedFeatures(e.point, {
        layers: ['clusters']
    });

    const clusterId = features[0].properties.cluster_id;

    // Ease the camera to the next cluster expansion
    map.getSource('earthquakes').getClusterExpansionZoom(
        clusterId,
        (err, zoom) => {
            if (!err) {
                map.easeTo({
                    center: features[0].geometry.coordinates,
                    zoom
                });
            }
        }
    );
});

For clustered sources, fetches the children of the given cluster on the next zoom level (as an array of GeoJSON features).
Parameters
Name	Description
clusterId
number
	The value of the cluster's cluster_id property.
callback
Function
	A callback to be called when the features are retrieved ( (error, features) => { ... } ).
Returns
GeoJSONSource: Returns itself to allow for method chaining.
Example

// Retrieve cluster children on click
// the clicked layer should be filtered to only include clusters, e.g. `filter: ['has', 'point_count']`
map.on('click', 'clusters', (e) => {
    const features = map.queryRenderedFeatures(e.point, {
        layers: ['clusters']
    });

    const clusterId = features[0].properties.cluster_id;

    clusterSource.getClusterChildren(clusterId, (error, features) => {
        if (!error) {
            console.log('Cluster children:', features);
        }
    });
});

For clustered sources, fetches the original points that belong to the cluster (as an array of GeoJSON features).
Parameters
Name	Description
clusterId
number
	The value of the cluster's cluster_id property.
limit
number
	The maximum number of features to return. Defaults to 10 if a falsy value is given.
offset
number
	The number of features to skip (for example, for pagination). Defaults to 0 if a falsy value is given.
callback
Function
	A callback to be called when the features are retrieved ( (error, features) => { ... } ).
Returns
GeoJSONSource: Returns itself to allow for method chaining.
Example

// Retrieve cluster leaves on click
// the clicked layer should be filtered to only include clusters, e.g. `filter: ['has', 'point_count']`
map.on('click', 'clusters', (e) => {
    const features = map.queryRenderedFeatures(e.point, {
        layers: ['clusters']
    });

    const clusterId = features[0].properties.cluster_id;
    const pointCount = features[0].properties.point_count;
    const clusterSource = map.getSource('clusters');

    clusterSource.getClusterLeaves(clusterId, pointCount, 0, (error, features) => {
    // Print cluster leaves in the console
        console.log('Cluster leaves:', error, features);
    });
});

Related

    Example: Draw GeoJSON points
    Example: Add a GeoJSON line
    Example: Create a heatmap from points
    Example: Create and style clusters 

Was this section on GeoJSONSource helpful?
ImageSource
githubsrc/source/image_source.ts

A data source containing an image. See the Style Specification for detailed documentation of options.
Extends Evented.
Example

// add to map
map.addSource('some id', {
    type: 'image',
    url: 'https://www.mapbox.com/images/foo.png',
    coordinates: [
        [-76.54, 39.18],
        [-76.52, 39.18],
        [-76.52, 39.17],
        [-76.54, 39.17]
    ]
});

// update coordinates
const mySource = map.getSource('some id');
mySource.setCoordinates([
    [-76.54335737228394, 39.18579907229748],
    [-76.52803659439087, 39.1838364847587],
    [-76.5295386314392, 39.17683392507606],
    [-76.54520273208618, 39.17876344106642]
]);

// update url and coordinates simultaneously
mySource.updateImage({
    url: 'https://www.mapbox.com/images/bar.png',
    coordinates: [
        [-76.54335737228394, 39.18579907229748],
        [-76.52803659439087, 39.1838364847587],
        [-76.5295386314392, 39.17683392507606],
        [-76.54520273208618, 39.17876344106642]
    ]
});

map.removeSource('some id');  // remove

Instance Members

Updates the image URL and, optionally, the coordinates. To avoid having the image flash after changing, set the raster-fade-duration paint property on the raster layer to 0.
Parameters
Name	Description
options
Object
	Options object.
options.coordinates
Array<Array<number>>?
	Four geographical coordinates, represented as arrays of longitude and latitude numbers, which define the corners of the image. The coordinates start at the top left corner of the image and proceed in clockwise order. They do not have to represent a rectangle.
options.url
string?
	Required image URL.
Returns
ImageSource: Returns itself to allow for method chaining.
Example

// Add to an image source to the map with some initial URL and coordinates
map.addSource('image_source_id', {
    type: 'image',
    url: 'https://www.mapbox.com/images/foo.png',
    coordinates: [
        [-76.54, 39.18],
        [-76.52, 39.18],
        [-76.52, 39.17],
        [-76.54, 39.17]
    ]
});
// Then update the image URL and coordinates
imageSource.updateImage({
    url: 'https://www.mapbox.com/images/bar.png',
    coordinates: [
        [-76.5433, 39.1857],
        [-76.5280, 39.1838],
        [-76.5295, 39.1768],
        [-76.5452, 39.1787]
    ]
});

Sets the image's coordinates and re-renders the map.
Parameters
Name	Description
coordinates
Array<Array<number>>
	Four geographical coordinates, represented as arrays of longitude and latitude numbers, which define the corners of the image. The coordinates start at the top left corner of the image and proceed in clockwise order. They do not have to represent a rectangle.
Returns
ImageSource: Returns itself to allow for method chaining.
Example

// Add an image source to the map with some initial coordinates
map.addSource('image_source_id', {
    type: 'image',
    url: 'https://www.mapbox.com/images/foo.png',
    coordinates: [
        [-76.54, 39.18],
        [-76.52, 39.18],
        [-76.52, 39.17],
        [-76.54, 39.17]
    ]
});
// Then update the image coordinates
imageSource.setCoordinates([
    [-76.5433, 39.1857],
    [-76.5280, 39.1838],
    [-76.5295, 39.1768],
    [-76.5452, 39.1787]
]);

Related

    Example: Add an image
    Example: Animate a series of images 

Was this section on ImageSource helpful?
ModelSource
github3d-style/source/model_source.ts

A source containing single models. See the Style Specification for detailed documentation of options.
Extends Evented.
Example

map.addSource('some id', {
  "type": "model",
  "models": {
    "ego-car" : {
         "uri": "car.glb",
         "position": [-74.0135, 40.7153],
         "orientation": [0, 0, 0],
         "materialOverrides": {
           "body": {
             "model-color": [0.00775, 0.03458, 0.43854],
             "model-color-mix-intensity": 1.0
           }
         },
         "nodeOverrides": {
           "doors_front-left": {
             "orientation": [0.0, -45.0, 0.0]
           }
         }
     }
  }
});

Instance Members

Sets the list of models along with their properties.

Updates are efficient as long as the model URIs remain unchanged.
Parameters
Name	Description
modelSpecs
ModelSourceModelsSpecification
	Model specifications according to Style Specification .
Example

map.getSource('some id').setModels({
    "model-1" : {
         "uri": "model_1.glb",
         "position": [-74.0135, 40.7153],
         "orientation": [0, 0, 0]
     }
});

Was this section on ModelSource helpful?
RasterArrayTileSource
githubsrc/source/raster_array_tile_source.ts

A data source containing raster-array tiles created with Mapbox Tiling Service. See the Style Specification for detailed documentation of options.
Extends RasterTileSource.
new RasterArrayTileSource(id: string, options: RasterArraySourceSpecification, dispatcher: Dispatcher, eventedParent: Evented)
Parameters
Name	Description
id
string
	
options
RasterArraySourceSpecification
	
dispatcher
Dispatcher
	
eventedParent
Evented
	
Example

// add to map
map.addSource('some id', {
    type: 'raster-array',
    url: 'mapbox://rasterarrayexamples.gfs-winds',
    tileSize: 512
});

Instance Members

When true, the source will only load the tile header and use range requests to load and parse the tile data. Otherwise, the entire tile will be loaded and parsed in the Worker.
Type
boolean
Related

    Example: Create a wind particle animation 

Was this section on RasterArrayTileSource helpful?
RasterTileSource
githubsrc/source/raster_tile_source.ts

A source containing raster tiles. See the Style Specification for detailed documentation of options.
Extends Evented.
new RasterTileSource(id: string, options: (RasterSourceSpecification | RasterDEMSourceSpecification | RasterArraySourceSpecification), dispatcher: Dispatcher, eventedParent: Evented)
Parameters
Name	Description
id
string
	
options
(RasterSourceSpecification | RasterDEMSourceSpecification | RasterArraySourceSpecification)
	
dispatcher
Dispatcher
	
eventedParent
Evented
	
Example

map.addSource('some id', {
    type: 'raster',
    url: 'mapbox://mapbox.satellite',
    tileSize: 256
});

map.addSource('some id', {
    type: 'raster',
    tiles: ['https://img.nj.gov/imagerywms/Natural2015?bbox={bbox-epsg-3857}&format=image/png&service=WMS&version=1.1.1&request=GetMap&srs=EPSG:3857&transparent=true&width=256&height=256&layers=Natural2015'],
    tileSize: 256
});

Instance Members

Reloads the source data and re-renders the map.
Example

map.getSource('source-id').reload();

Sets the source tiles property and re-renders the map.
Parameters
Name	Description
tiles
Array<string>
	An array of one or more tile source URLs, as in the TileJSON spec.
Returns
RasterTileSource: Returns itself to allow for method chaining.
Example

map.addSource('source-id', {
    type: 'raster',
    tiles: ['https://some_end_point.net/{z}/{x}/{y}.png'],
    tileSize: 256
});

// Set the endpoint associated with a raster tile source.
map.getSource('source-id').setTiles(['https://another_end_point.net/{z}/{x}/{y}.png']);

Sets the source url property and re-renders the map.
Parameters
Name	Description
url
string
	A URL to a TileJSON resource. Supported protocols are http: , https: , and mapbox://<Tileset ID> .
Returns
RasterTileSource: Returns itself to allow for method chaining.
Example

map.addSource('source-id', {
    type: 'raster',
    url: 'mapbox://mapbox.satellite'
});

// Update raster tile source to a new URL endpoint
map.getSource('source-id').setUrl('mapbox://mapbox.satellite');

Related

    Example: Add a raster tile source
    Example: Add a WMS source 

Was this section on RasterTileSource helpful?
VectorTileSource
githubsrc/source/vector_tile_source.ts

A source containing vector tiles in Mapbox Vector Tile format. See the Style Specification for detailed documentation of options.
Extends Evented.
new VectorTileSource(id: string, options: any, dispatcher: Dispatcher, eventedParent: Evented)
Parameters
Name	Description
id
string
	
options
any
	
dispatcher
Dispatcher
	
eventedParent
Evented
	
Example

map.addSource('some id', {
    type: 'vector',
    url: 'mapbox://mapbox.mapbox-streets-v8'
});

map.addSource('some id', {
    type: 'vector',
    tiles: ['https://d25uarhxywzl1j.cloudfront.net/v0.1/{z}/{x}/{y}.mvt'],
    minzoom: 6,
    maxzoom: 14
});

map.getSource('some id').setUrl("mapbox://mapbox.mapbox-streets-v8");

map.getSource('some id').setTiles(['https://d25uarhxywzl1j.cloudfront.net/v0.1/{z}/{x}/{y}.mvt']);

Instance Members

Reloads the source data and re-renders the map.
Example

map.getSource('source-id').reload();

Sets the source tiles property and re-renders the map.
Parameters
Name	Description
tiles
Array<string>
	An array of one or more tile source URLs, as in the TileJSON spec.
Returns
VectorTileSource: Returns itself to allow for method chaining.
Example

map.addSource('source-id', {
    type: 'vector',
    tiles: ['https://some_end_point.net/{z}/{x}/{y}.mvt'],
    minzoom: 6,
    maxzoom: 14
});

// Set the endpoint associated with a vector tile source.
map.getSource('source-id').setTiles(['https://another_end_point.net/{z}/{x}/{y}.mvt']);

Sets the source url property and re-renders the map.
Parameters
Name	Description
url
string
	A URL to a TileJSON resource. Supported protocols are http: , https: , and mapbox://<Tileset ID> .
Returns
VectorTileSource: Returns itself to allow for method chaining.
Example

map.addSource('source-id', {
    type: 'vector',
    url: 'mapbox://mapbox.mapbox-streets-v7'
});

// Update vector tile source to a new URL endpoint
map.getSource('source-id').setUrl("mapbox://mapbox.mapbox-streets-v8");

Related

    Example: Add a vector tile source
    Example: Add a third party vector tile source 

Was this section on VectorTileSource helpful?
VideoSource
githubsrc/source/video_source.ts

A data source containing video. See the Style Specification for detailed documentation of options.
Extends ImageSource.
Example

// add to map
map.addSource('some id', {
    type: 'video',
    url: [
        'https://www.mapbox.com/blog/assets/baltimore-smoke.mp4',
        'https://www.mapbox.com/blog/assets/baltimore-smoke.webm'
    ],
    coordinates: [
        [-76.54, 39.18],
        [-76.52, 39.18],
        [-76.52, 39.17],
        [-76.54, 39.17]
    ]
});

// update
const mySource = map.getSource('some id');
mySource.setCoordinates([
    [-76.54335737228394, 39.18579907229748],
    [-76.52803659439087, 39.1838364847587],
    [-76.5295386314392, 39.17683392507606],
    [-76.54520273208618, 39.17876344106642]
]);

map.removeSource('some id');  // remove

Instance Members

Pauses the video.
Example

// Assuming a video source identified by video_source_id was added to the map
const videoSource = map.getSource('video_source_id');

// Pauses the video
videoSource.pause();

Plays the video.
Example

// Assuming a video source identified by video_source_id was added to the map
const videoSource = map.getSource('video_source_id');

// Starts the video
videoSource.play();

Returns the HTML video element.
Returns
HTMLVideoElement: The HTML video element.
Example

// Assuming a video source identified by video_source_id was added to the map
const videoSource = map.getSource('video_source_id');

videoSource.getVideo(); // <video crossorigin="Anonymous" loop="">...</video>

Sets the video's coordinates and re-renders the map.
Returns
VideoSource: Returns itself to allow for method chaining.
Example

// Add a video source to the map to map
map.addSource('video_source_id', {
    type: 'video',
    urls: [
        'https://www.mapbox.com/blog/assets/baltimore-smoke.mp4',
        'https://www.mapbox.com/blog/assets/baltimore-smoke.webm'
    ],
    coordinates: [
        [-76.54, 39.18],
        [-76.52, 39.18],
        [-76.52, 39.17],
        [-76.54, 39.17]
    ]
});

// Then update the video source coordinates by new coordinates
const videoSource = map.getSource('video_source_id');
videoSource.setCoordinates([
    [-76.5433, 39.1857],
    [-76.5280, 39.1838],
    [-76.5295, 39.1768],
    [-76.5452, 39.1787]
]);

Related

    Example: Add a video 

Was this section on VideoSource helpful?
Was this page helpful?
© Mapbox All Rights Reserved
Terms
Privacy
Security
Your California Privacy Choices

Projections
On this page

    Map Projections
    Use projections in Mapbox GL JS
        What projections are available?
        Define a projection as a Map constructor option
        Set a projection at runtime
        Define a projection in a style
        Get current map projection
    Adaptive Projection Behavior
        Map “unskewing” on zoom
        Zoom and bearing
        Constraining interaction
    Limitations of Adaptive Projections
        3D and Background styling
        Custom style layers
    Thematic Projections
        Equal Earth
        Natural Earth
        Winkel Tripel
    Conic Projections
        Albers
        Lambert conformal conic
        Customize a conic projection
    Rectangular Projections
        Equirectangular
        Mercator
    Globe

Equal Earth projection in GL JS v2

Starting from v2.6, Mapbox GL JS supports multiple map projections. This feature allows you to create more accurate visualizations at every zoom level and tell a better story with your data.
Default projection for styles

In the latest Mapbox styles, Globe is the default projection.
Map Projections

A map projection is a way to flatten the planet's surface onto a page or screen. Every projection has strengths and weaknesses, so the right projection depends on your use case.

For most maps, we recommend using globe to accurately represent locations on the Earth. The most notable limitation of globe is that only half the earth is visible onscreen at once. If you're building a static map or data visualization, an alternative projection might be a good choice.

Mapbox GL JS provides a variety of alternative "adaptive" projections, including projections optimized for thematic world maps, and projections for representing specific regions (such as the contiguous U.S. or Europe).
Use projections in Mapbox GL JS

Projections are compatible with all tile sources and most map styles (with a few caveats below). See this example to get started quickly, or explore all available projections in this more advanced example.

You can set the projection by editing the map style in Mapbox Studio, with the map constructor’s projection option, or at runtime via the setProjection method. Mapbox v12 styles include the Globe projection by default. Maps with no projection set default to the Mercator projection.
What projections are available?

Developers can select any of the following options when defining a style (each projection is defined in more detail below):

    Globe: A 3D representation of the Earth.
        globe, the default in v12 styles
    Thematic: Curved map edges create a pleasing aesthetic suggesting classic world maps. A good choice for world-scale thematic maps.
        Equal-area: Relative size of regions is accurate, but shapes are distorted. - equalEarth - Compromise: A balance of shape and size distortion. - naturalEarth - winkelTripel
    Conic: Distortion is minimized in one area. A good choice for maps limited to a specific country or region.
        Equal-area: Relative area is accurate, but shapes are distorted.
            albers
        Conformal: Shapes and angles are accurate, but sizes are distorted.
            lambertConformalConic
    Rectangular: These projections can loop across the 180th Meridian, useful for viewing the Pacific ocean. Known as cylindrical projections in cartography.
        Compromise: A balance of shape and size distortion.
            equirectangular
        Conformal: Shapes and angles are accurate, but sizes are distorted.
            mercator, the default if not set in style

Define a projection as a Map constructor option

You can define a map projection when creating a Map instance using shorthand:

const map = new mapboxgl.Map({
  container: 'map',
  projection: 'naturalEarth'
});

Set a projection at runtime

You can set or change the map’s projection after Map creation by using the setProjection method:

// Use shorthand with default parameters
map.setProjection('equalEarth');

// Or override the projection-specific options
map.setProjection({
  name: 'albers',
  center: [41.33, 123.45],
  parallels: [30, 50]
});

Define a projection in a style

You can define a projection in a map style:

const map = new mapboxgl.Map({
  style: {
    version: 8,
    name: 'My Projected Style',
    sources: {
      // ...
    },
    layers: [
      // ...
    ],
    projection: {
      name: 'equalEarth'
    }
  }
});

Important notes about using projections in a style:

    A projection defined in a style must be an object. The string shorthand is not valid in a style specification.
    If you define one projection in a style, and set a different one at runtime (either through the map’s constructor or setProjection), then the runtime projection will be used.
    Calling map.setProjection(null) will revert from any runtime projection to the one defined in the style.

Get current map projection

Developers can get the current map’s projection using map.getProjection().
Adaptive Projection Behavior
Map “unskewing” on zoom

Adaptive projections in Mapbox GL JS (all projections besides globe and Mercator) have a novel adaptive design that adjusts the projection as you zoom in to reduce distortion at all zoom levels by gradually transitioning from the defined projection to Web Mercator (which is optimal on higher zooms).
Zoom and bearing

For any camera zoom level and location, maps in adaptive projections will be rendered at the same scale they would be rendered in Mercator.

The bearing in rectangular projections corresponds directly to the rotation of the map (north is up). In thematic and conic projections, the concept of bearing is more complicated since the direction of north can be different at different points on the map:

    At low zoom levels, the bearing corresponds to the direction of north at the center of the projection.
    At high zoom levels, the bearing corresponds to the direction of north at the center of the screen.
    At intermediate zoom levels, bearing transitions between the two meanings.

PLAYGROUND
Location Helper

To experiment with camera pitch, bearing, tilt, and zoom and get values to use in your code, try our Location Helper tool.
Constraining interaction

Maximum bounds constraints work differently with adaptive projections. Map panning and zooming is constrained in a way so that the center of the map doesn’t go beyond the specified geographic bounds, rather than the whole visible area. We may revisit this behavior in a future release.
Limitations of Adaptive Projections

Adaptive projections don't support all features supported by Globe and Mercator. We plan to add support for these features in a future release.
3D and Background styling

3D terrain and Free Camera API can only be used with Globe and Mercator.

Atmospheric styling is also supported only in globe and Mercator projections. In other projections, the empty area around the world is always rendered as transparent and can be styled by changing the CSS background property on the map container.
Custom style layers

CustomLayerInterface can only be used only with Mercator.
Thematic Projections

In these following three projections, curved map edges create a pleasant rounded aesthetic suggesting classic world maps. These projections are good choices for data visualization on a global scale.

Equal Earth and Natural Earth are Pseudocylindrical projections, with straight lines of latitude and curved lines of longitude. Winkel Tripel is a Pseudoazimuthal projection with lines of latitude bending slightly inward.
Equal Earth
Equal Earth projection in Mapbox GL JS

The Equal Earth projection (defined as equalEarth in the Mapbox GL JS API) is a pseudocylindrical, equal-area projection. This projection accurately reflects sizes and is thus especially useful in data visualization when it's important to make regional size comparisons.

A notable use of Equal Earth projection is thematic maps on global temperature anomalies by NASA.
Natural Earth
Natural Earth projection in Mapbox GL JS

The Natural Earth projection (defined as naturalEarth in the Mapbox GL JS API) is a pseudocylindrical, compromise projection. This projection looks much like Equal Earth but displays a more "natural" appearance by minimizing shape distortion at the cost of a small amount of size distortion.
Winkel Tripel
Winkel Tripel projection in Mapbox GL JS

The Winkel Tripel projection (defined as winkelTripel in the Mapbox GL JS API) is a “modified azimuthal” compromise projection. The “tripel” part of the name comes from its goal of minimizing distortion in three aspects: area, direction and distance.

Winkel Tripel appears taller and more rounded than Equal Earth and Natural Earth, and provides more accurate shapes with less accurate sizes. Winkel Tripel is commonly regarded as one of the least distorted compromise projections. The National Geographic Society and many other educational institutions use Winkel Tripel for global thematic mapping.

The curved latitude lines in Winkel Tripel make it unsuitable for maps where comparing latitude is important.
Conic Projections

Conic projections create a map with little distortion in the area around a specific point. Further away from this point, distortion increases. In albers, this is shape distortion, while in lambertConformalConic size increases with greater distance.

This area can be placed anywhere on the earth as described below.
Albers
Albers projection in Mapbox GL JS

The Albers projection (defined as albers in the Mapbox GL JS API) is a conic, equal-area projection. Like Equal Earth, this projection provides accurate relative sizes, but shapes are increasingly distorted at further distances.

By default, the Albers projection is centered on the mainland United States at [-96, 37.5] with the standard parallels [29.5, 45.5]. This “Albers USA” projection is commonly used for showing geographic data in which comparing state-level sizes is important, for example in U.S. elections. Notable users of the projection include U.S. Geographical Survey, U.S. Census Bureau, and National Atlas of the U.S.

Composite Albers projection (for example where Alaska and Hawaii are alongside the mainland U.S.) is not yet supported in Mapbox GL JS.
Lambert conformal conic
Lambert Conformal Conic projection in Mapbox GL JS

The Lambert conformal conic projection (defined as lambertConformalConic in the Mapbox GL JS API) is a conic, conformal projection used for aeronautical charts and many regional mapping systems. Like Mercator, this is a conformal projection, meaning that shapes and angles are accurately represented. Instead, regions further away from the center are increasingly exaggerated in size.

By default, this projection is centered on [0, 30] with the standard parallels [30, 30]. This projection preserves shapes and is appropriate for regional maps which need accurate shapes and angles (note that as with many other conformal projections, size distortion will increase towards the poles).

This projection is popular for aeronautical charts because straight lines on it approximate great circle routes between endpoints. Notable users include the European Environmental Agency, France, and also U.S. National Geodetic Survey for several U.S. states such as Tennessee.
Customize a conic projection

By configuring center and parallels properties, a developer can choose where to place the area of minimized distortion.

    parallels: [latitude1, latitude2]: Distortion of area and shape is reduced by the projection in the region between these two lines of latitude. The parallels can be the same latitude.
    center: [longitude, latitude]: The location used to match scale and bearing with mercator. The size and bearing at this location will always be the same as it would be in mercator at the same zoom. At low zoom levels, other locations may have distorted size and bearing.

These properties can also be defined in the setProjection method or in a style.

This example shows how to configure the Albers projection to center on the U.S. state of Alaska:

const map = new mapboxgl.Map({
  container: 'map',
  projection: {
    name: 'albers',
    center: [-154, 50],
    parallels: [55, 65]
  }
});

A polar projection can be created by setting both parallel latitudes to 90 (for the North Pole) or -90 (for the South Pole). For instance, to create a conformal polar projection centered on Greenland:

const map = new mapboxgl.Map({
  container: 'map',
  projection: {
    name: 'lambertConformalConic',
    center: [-40, 0],
    parallels: [90, 90]
  }
});

For any projection besides Albers and Lambert conformal conic, the center and parallels properties will be ignored.
Rectangular Projections

Equirectangular and Mercator are classified in cartography as cylindrical projections. These projections have straight latitude and longitude lines. Their rectangular shape allows them to loop across their east and west edges at the 180th Meridian, useful for maps that need to cover the Pacific ocean. Looping can also be disabled with setRenderWorldCopies.
Equirectangular
Equirectangular projection in Mapbox GL JS

The Equirectangular (Plate Carrée) projection (defined as equirectangular in the Mapbox GL JS API) is a cylindrical, compromise projection in which positions on the map directly correspond to their longitude and latitude values.

Equirectangular is useful for mapping the Pacific ocean while minimizing the size distortion of Mercator.

This projection is the standard for global raster datasets, such as Celestia, NASA World Wind, and Natural Earth, and is useful for displaying these datasets without distortion.
Mercator
Equirectangular projection in Mapbox GL JS

The Web Mercator projection (defined as mercator in the Mapbox GL JS API) is a cylindrical, conformal projection and the default projection in Mapbox GL JS if projection is not specified in a style. Web Mercator is classified as EPSG:3857 and is a variant of the classic Mercator projection used for marine navigation. Web Mercator was the first projection introduced in web maps and remains widely used by most mapping platforms. Before the introduction of adaptive projections in v2.6, Mapbox GL JS only supported the Web Mercator projection.

Mercator accurately displays shapes and angles, which makes it useful for navigation. At the world scale, it exaggerates the size of geographic shapes near the poles. For example, Greenland appears the same size as Africa, even though it’s 14 times smaller.

Mercator is suitable for maps remaining at high zoom or cases where a map needs to cover the 180th meridian. In Mapbox GL JS, Mercator also supports some features unavailable in other projections as outlined above.
Globe
Globe View projection in Mapbox GL JS

The Globe projection (defined as globe in the Mapbox GL JS API) is a three-dimensional representation of the earth. Globe increases the sense of depth of the map and is a correct representation of the surface of the earth as viewed from space. Using this projection limits the display of the earth to one hemisphere at a time. This can be addressed in some cases by rotating the globe with camera animation.

In Mapbox GL JS, Globe is the default projection in most of the latest Mapbox styles. Globe supports some functionality that adaptive projections do not. This includes Fog/atmospheric styling, 3D terrain and Free Camera.

Learn more about globe in the Globe and Atmosphere guide.