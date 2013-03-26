<table name="tracklist" class="table table-hover">
  <thead>
    <tr><th>Track</th><th>Artist</th><th>Album</th></tr>
  </thead>
{{#each tracks}}
    <tr class="track_item" data-mp3="{{this.mp3_stream_url}}" data-ogg="{{this.ogg_stream_url}}" data-url="{{ this.resource_uri }}" data-delete><td>{{this.title}} <div class="dropdown pull-right"><i role="button" class="icon-cog dropdown-toggle" data-toggle="dropdown"></i>{{> trackDropdown}}</div></td><td><a href="#artist/{{this.album.artist.id}}">{{this.album.artist.name}}</a></td><td><a href="#album/{{this.album.id}}">{{this.album.title}}</a></td></tr>
{{/each}}
</table>