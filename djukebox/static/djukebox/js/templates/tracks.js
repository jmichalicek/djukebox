<table name="tracklist" class="table table-hover">
  <thead>
    <tr><th>Track</th><th>Artist</th><th>Album</th></tr>
  </thead>
{{#each tracks}}
    <tr class="track_item" mp3="{{this.mp3_stream_url}}" ogg="{{this.ogg_stream_url}}"><td>{{this.title}}</td><td>{{this.album.artist.name}}</td><td>{{this.album.name}}</td></tr>
{{/each}}
</table>