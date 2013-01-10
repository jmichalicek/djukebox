<div class="span2 thumbnail" style="height: 25%">
<!-- album art to go here -->
    <h3>{{title}}</h3><br />
    <h5><a href="#artist/{{artist.id}}/">{{artist.name}}</a></h5>
    <!-- add more details -->
</div>
<div class="span10">
  {{#each tracks }}
  <div id="{{this.id}}" class="thumbnail track_item" data-mp3="{{this.mp3_stream_url}}" data-ogg="{{this.ogg_stream_url}}" data-delete>
    {{this.title}}
    <div class="dropdown pull-right"><i role="button" class="icon-cog dropdown-toggle" data-toggle="dropdown"></i>{{> trackDropdown}}</div>
  </div>
  {{/each}}
</div>
