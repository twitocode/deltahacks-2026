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
