<div align=center>
	<h1>Rendering Denoising camera Light Master Tool</br>RDCL Master</h1>
	<p>
		Written and maintained by Philip Wersonig / Rauhm</br>
		See more of my work under <a href="https://www.wersonig.at">www.wersonig.at</a>
	</p>
</div>

<div>
	<h2>This tools purpose.</h2>
	<p>This collection of tools has been written for my personal use, and made public to make it easier for new Camera and Lighting Artists to safe time with repetitve parts of setting up and post producing scenes, which don't have access to large inhouse libaries managing those elements.</p>
	<p>These libraries are primarily setup for myself and to work with my workflow. </p>
	<p>If someone else finds usage in what I have written for myself, feel free to use it and where possible and appropriate credit me in a small way.</p>
	<p>I do not promise to keep these libraries up to date, relevant or improve on them in any major way, but if someone finds any bugs, or has ideas on how to improve the tools, throw them somewhere here and if there is enough traction I'll see what can be done.</p>
</div>

<div>
	<h2>Compatability.</h2>
	<ul>
		<li>The tools have been tested to work on Maya 2024 with python3</li>
		<li>The tools <b>should</b>  work on Maya 2024 with python2</li>
	</ul>
</div>

<div>
	<h2>Installation.</h2>
	<ol>
		<li>Download this folder over github or pull the repository.</li>
		<li>Drop the entire folder in a location you are not going to move later.</li>
		<li>Everyone who wants to use the tools has to drag the "drag-and-drop-install.mel" or "drag-and-drop-install.py" file into their maya viewport.</li>
		<li>Restart maya and enjoy. (the shelf with all tools being setup should be automatically loaded on restart. As well as all the functions working.)</li>
	</ol>
</div>

<div>
	<h2>What is in the Box.</h2>
	<p>A brief listing of everything this collection can do.</p>
</div>

<div>
	<h3>Camera Related.</h3>
	<h4>Tear off copy Camera</h4>
	<p>
		A reinvisoning of mayas default ability to tear off and copy the currently active camera.</br>
		This version allows to select the camera in the viewport and additionally to only copying the cameras view also locks it as well as activating the resolution and filmgate.</br>
		</br>
		Right now this tool only works when the viewport is the currently active window.</br>
		To use: click the camera > click the viewport > click the tool in the shelf.
		</p>
</div>

<div>
	<h3>Light Related.</h3>
	<h4>Set Light to LightGroup AOV Name</h4>
	<p>
		A tool to automatically set the Lights related AOV Group to the name of Light Object</br>
		Double-Click opens the config window with which you can control how it sets the AOV Name / i.e. which part of the Light Objects name it uses, aswell as which types of lights it edits. Per default it only edits Arnold Lights.
	</p>
</div>

<div>
	<h3>Rendering Related.</h3>
	<h4>Deactivate All AOVs</h4>
	<p>A simple tool creating in the currently active render layer an absolut override for every AOV deactivating them for this render layer.</p>
	<h4>Remove All AOVs</h4>
	<p>My Implementation of the Delete All AOV Button.</p>
	<h4>Copy AOVs for Denoising</h4>
	<p>A tool Copying all AVOs names prepped for further use in either a denoising script or the Arnold Noice Denosier.</p>
	<h4>AOV Master Tool</h4>
	<p>A tool making the AOV creation easier. Allowing also the use of pre defined custom AOV presets to quick create detailed AOV Pipelines, keeping the detailed AOV Group Spreading whithout having to set it up everytime for every scene.  </p>
</div>

<div>
	<h3>Denoising Related.</h3>
	<h4>None</h4>
	<p>Yet to be added</p>
</div>
