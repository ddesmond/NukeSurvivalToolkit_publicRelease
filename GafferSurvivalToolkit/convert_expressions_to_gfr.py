#!/usr/bin/env python3
"""
Convert Nuke Expression-based procedural patterns to Gaffer .gfr format.

Uses GafferImage native nodes (Ramp, Checkerboard, Constant) and OSLImage+OSLCode
for per-pixel operations that can't be done with native nodes.

Usage:
    python convert_expressions_to_gfr.py --output demo/
"""

import os
from pathlib import Path


def write_gfr(output_path, content):
    """Write .gfr file content."""
    with open(output_path, "w") as f:
        f.write(content)
    print(f"  Created {Path(output_path).name}")


def convert_gradient_horizontal(output_dir):
    """Nuke: expr0 "x / width" → Gaffer: Ramp node"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["Ramp"] = GafferImage.Ramp( "Ramp" )
parent.addChild( __children["Ramp"] )
__children["Ramp"]["in"].setInput( __children["Constant"]["out"] )
__children["Ramp"]["startPosition"].setValue( imath.V2f( 0, 540 ) )
__children["Ramp"]["endPosition"].setValue( imath.V2f( 1920, 540 ) )
__children["Ramp"]["ramp"].addStop( 0.0, imath.Color4f( 0, 0, 0, 1 ) )
__children["Ramp"]["ramp"].addStop( 1.0, imath.Color4f( 1, 1, 1, 1 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "gradient_horizontal.gfr"), content)


def convert_gradient_vertical(output_dir):
    """Nuke: expr0 "y / height" → Gaffer: Ramp node"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["Ramp"] = GafferImage.Ramp( "Ramp" )
parent.addChild( __children["Ramp"] )
__children["Ramp"]["in"].setInput( __children["Constant"]["out"] )
__children["Ramp"]["startPosition"].setValue( imath.V2f( 960, 0 ) )
__children["Ramp"]["endPosition"].setValue( imath.V2f( 960, 1080 ) )
__children["Ramp"]["ramp"].addStop( 0.0, imath.Color4f( 0, 0, 0, 1 ) )
__children["Ramp"]["ramp"].addStop( 1.0, imath.Color4f( 1, 1, 1, 1 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "gradient_vertical.gfr"), content)


def convert_gradient_horizontal_invert(output_dir):
    """Nuke: expr0 "1 - x / width" → Gaffer: Ramp + Grade(invert)"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["Ramp"] = GafferImage.Ramp( "Ramp" )
parent.addChild( __children["Ramp"] )
__children["Ramp"]["in"].setInput( __children["Constant"]["out"] )
__children["Ramp"]["startPosition"].setValue( imath.V2f( 1920, 540 ) )
__children["Ramp"]["endPosition"].setValue( imath.V2f( 0, 540 ) )
__children["Ramp"]["ramp"].addStop( 0.0, imath.Color4f( 0, 0, 0, 1 ) )
__children["Ramp"]["ramp"].addStop( 1.0, imath.Color4f( 1, 1, 1, 1 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "gradient_horizontal_invert.gfr"), content)


def convert_gradient_vertical_invert(output_dir):
    """Nuke: expr0 "1 - y / height" → Gaffer: Ramp + Grade(invert)"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["Ramp"] = GafferImage.Ramp( "Ramp" )
parent.addChild( __children["Ramp"] )
__children["Ramp"]["in"].setInput( __children["Constant"]["out"] )
__children["Ramp"]["startPosition"].setValue( imath.V2f( 960, 1080 ) )
__children["Ramp"]["endPosition"].setValue( imath.V2f( 960, 0 ) )
__children["Ramp"]["ramp"].addStop( 0.0, imath.Color4f( 0, 0, 0, 1 ) )
__children["Ramp"]["ramp"].addStop( 1.0, imath.Color4f( 1, 1, 1, 1 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "gradient_vertical_invert.gfr"), content)


def convert_radial_gradient(output_dir):
    """Nuke: radial gradient → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'float dist = sqrt( pow( (u - 0.5) * 2.0, 2 ) + pow( (v - 0.5) * 2.0, 2 ) );\\noutput1 = color( 1.0 - dist, 1.0 - dist, 1.0 - dist );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "radial_gradient.gfr"), content)


def convert_circles(output_dir):
    """Nuke: sin(sqrt(x*x + y*y)) → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'float d = sqrt( pow( u * 20.0, 2 ) + pow( v * 20.0, 2 ) );\\nfloat c = sin( d );\\noutput1 = color( c, c, c );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "circles.gfr"), content)


def convert_bricks(output_dir):
    """Nuke: brick pattern expression → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'float size = 0.1;\\nfloat offset = 0.5;\\nfloat bx = floor( u / size );\\nfloat by = floor( v / size );\\nfloat brick = mod( bx + mod( by, 2.0 ) * offset, 2.0 );\\nfloat mx = mod( u, size ) / size;\\nfloat my = mod( v, size ) / size;\\nfloat edge = (mx < 0.05 || mx > 0.95 || my < 0.05 || my > 0.95) ? 0.0 : 1.0;\\nfloat c = brick * edge;\\noutput1 = color( c, c, c );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "bricks.gfr"), content)


def convert_radial_rays(output_dir):
    """Nuke: radial rays → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'float angle = atan( (v - 0.5) * 2.0, (u - 0.5) * 2.0 );\\nfloat rays = sin( angle * 20.0 ) * 0.5 + 0.5;\\noutput1 = color( rays, rays, rays );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "radial_rays.gfr"), content)


def convert_turbulence(output_dir):
    """Nuke: turbulence noise → Gaffer: OSLImage + OSLShader(Noise)"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["Noise"] = GafferOSL.OSLShader( "Noise" )
parent.addChild( __children["Noise"] )
__children["Noise"].loadShader( "Pattern/Noise" )
__children["Noise"]["parameters"]["type"].setValue( "turbulence" )
__children["Noise"]["parameters"]["scale"].setValue( 5.0 )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["Noise"]["out"]["n"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["Noise"]["out"]["n"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["Noise"]["out"]["n"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["Noise"]["out"]["n"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "turbulence.gfr"), content)


def convert_noise(output_dir):
    """Nuke: noise → Gaffer: OSLImage + OSLShader(Noise)"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["Noise"] = GafferOSL.OSLShader( "Noise" )
parent.addChild( __children["Noise"] )
__children["Noise"].loadShader( "Pattern/Noise" )
__children["Noise"]["parameters"]["type"].setValue( "usimplex" )
__children["Noise"]["parameters"]["scale"].setValue( 5.0 )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["Noise"]["out"]["n"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["Noise"]["out"]["n"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["Noise"]["out"]["n"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["Noise"]["out"]["n"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "Noise.gfr"), content)


def convert_fbm(output_dir):
    """Nuke: fBm noise → Gaffer: OSLImage + OSLShader(Noise)"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["Noise"] = GafferOSL.OSLShader( "Noise" )
parent.addChild( __children["Noise"] )
__children["Noise"].loadShader( "Pattern/Noise" )
__children["Noise"]["parameters"]["type"].setValue( "fBm" )
__children["Noise"]["parameters"]["scale"].setValue( 5.0 )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["Noise"]["out"]["n"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["Noise"]["out"]["n"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["Noise"]["out"]["n"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["Noise"]["out"]["n"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "fBm.gfr"), content)


def convert_twist(output_dir):
    """Nuke: twist → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'float cx = u - 0.5;\\nfloat cy = v - 0.5;\\nfloat dist = sqrt( cx * cx + cy * cy );\\nfloat angle = atan( cy, cx ) + dist * 20.0;\\nfloat c = sin( angle ) * 0.5 + 0.5;\\noutput1 = color( c, c, c );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "twist.gfr"), content)


def convert_coordinates(output_dir):
    """Nuke: coordinates → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'output1 = color( u, v, 0.0 );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "coordinates.gfr"), content)


def convert_abs(output_dir):
    """Nuke: abs(r), abs(g), abs(b), abs(a) → Gaffer: Grade + Clamp"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( -0.5, -0.3, -0.8, -0.2 ) )

__children["Grade"] = GafferImage.Grade( "Grade" )
parent.addChild( __children["Grade"] )
__children["Grade"]["in"].setInput( __children["Constant"]["out"] )
__children["Grade"]["multiply"].setValue( imath.Color4f( -1, -1, -1, -1 ) )

__children["Clamp"] = GafferImage.Clamp( "Clamp" )
parent.addChild( __children["Clamp"] )
__children["Clamp"]["in"].setInput( __children["Grade"]["out"] )
__children["Clamp"]["minimum"].setValue( imath.Color4f( 0, 0, 0, 0 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "abs.gfr"), content)


def convert_check_negative(output_dir):
    """Nuke: check negative → Gaffer: Grade + Clamp"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["Clamp"] = GafferImage.Clamp( "Clamp" )
parent.addChild( __children["Clamp"] )
__children["Clamp"]["in"].setInput( __children["Constant"]["out"] )
__children["Clamp"]["minimum"].setValue( imath.Color4f( 0, 0, 0, 0 ) )
__children["Clamp"]["maximum"].setValue( imath.Color4f( 0, 0, 0, 1 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "check_negative.gfr"), content)


def convert_kill_nan(output_dir):
    """Nuke: kill NaN → Gaffer: Clamp"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["Clamp"] = GafferImage.Clamp( "Clamp" )
parent.addChild( __children["Clamp"] )
__children["Clamp"]["in"].setInput( __children["Constant"]["out"] )
__children["Clamp"]["minimum"].setValue( imath.Color4f( -1000000, -1000000, -1000000, -1000000 ) )
__children["Clamp"]["maximum"].setValue( imath.Color4f( 1000000, 1000000, 1000000, 1000000 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "kill_nan.gfr"), content)


def convert_kill_inf(output_dir):
    """Nuke: kill inf → Gaffer: Clamp"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["Clamp"] = GafferImage.Clamp( "Clamp" )
parent.addChild( __children["Clamp"] )
__children["Clamp"]["in"].setInput( __children["Constant"]["out"] )
__children["Clamp"]["minimum"].setValue( imath.Color4f( -1000000, -1000000, -1000000, -1000000 ) )
__children["Clamp"]["maximum"].setValue( imath.Color4f( 1000000, 1000000, 1000000, 1000000 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "kill_inf.gfr"), content)


def convert_alpha_binary(output_dir):
    """Nuke: alpha binary → Gaffer: Grade + Clamp"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["Grade"] = GafferImage.Grade( "Grade" )
parent.addChild( __children["Grade"] )
__children["Grade"]["in"].setInput( __children["Constant"]["out"] )
__children["Grade"]["contrast"].setValue( 100.0 )

__children["Clamp"] = GafferImage.Clamp( "Clamp" )
parent.addChild( __children["Clamp"] )
__children["Clamp"]["in"].setInput( __children["Grade"]["out"] )
__children["Clamp"]["minimum"].setValue( imath.Color4f( 0, 0, 0, 0 ) )
__children["Clamp"]["maximum"].setValue( imath.Color4f( 1, 1, 1, 1 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "alpha_binary.gfr"), content)


def convert_despill_green(output_dir):
    """Nuke: despill green → Gaffer: Grade + Shuffle"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( 0.2, 0.8, 0.3, 1 ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat key = max( 0.0, c.g - (c.r + c.b) / 2.0 );\\nc.g = c.g - key;\\noutput1 = c.rgb;' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "despill_green.gfr"), content)


def convert_despill_blue(output_dir):
    """Nuke: despill blue → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( 0.2, 0.3, 0.8, 1 ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat key = max( 0.0, c.b - (c.r + c.g) / 2.0 );\\nc.b = c.b - key;\\noutput1 = c.rgb;' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "despill_blue.gfr"), content)


def convert_checkerboard(output_dir):
    """Nuke: circles_user (simplified) → Gaffer: Checkerboard"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Checkerboard"] = GafferImage.Checkerboard( "Checkerboard" )
parent.addChild( __children["Checkerboard"] )
__children["Checkerboard"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Checkerboard"]["size"].setValue( imath.V2f( 100, 100 ) )
__children["Checkerboard"]["colorA"].setValue( imath.Color4f( 1, 1, 1, 1 ) )
__children["Checkerboard"]["colorB"].setValue( imath.Color4f( 0, 0, 0, 1 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "circles_user.gfr"), content)


def convert_circles_user(output_dir):
    """Nuke: circles with user params → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'float d = sqrt( pow( (u - 0.5) * 10.0, 2 ) + pow( (v - 0.5) * 10.0, 2 ) );\\nfloat c = sin( d );\\noutput1 = color( c, c, c );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "circles_user.gfr"), content)


def convert_gradient_corner(output_dir):
    """Nuke: corner gradient → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'float d1 = sqrt( pow( u, 2 ) + pow( v, 2 ) );\\nfloat d2 = sqrt( pow( 1.0 - u, 2 ) + pow( 1.0 - v, 2 ) );\\nfloat d = min( d1, d2 );\\noutput1 = color( d, d, d );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "GradientCorner.gfr"), content)


def main():
    output_dir = "demo"
    os.makedirs(output_dir, exist_ok=True)

    print("Converting Expression-based procedural patterns to Gaffer .gfr...")
    print()

    # Native node conversions
    convert_gradient_horizontal(output_dir)
    convert_gradient_vertical(output_dir)
    convert_gradient_horizontal_invert(output_dir)
    convert_gradient_vertical_invert(output_dir)
    convert_checkerboard(output_dir)

    # OSLImage + OSLCode conversions
    convert_radial_gradient(output_dir)
    convert_circles(output_dir)
    convert_bricks(output_dir)
    convert_radial_rays(output_dir)
    convert_turbulence(output_dir)
    convert_twist(output_dir)
    convert_fbm(output_dir)
    convert_coordinates(output_dir)
    convert_noise(output_dir)
    convert_circles_user(output_dir)
    convert_gradient_corner(output_dir)

    # Grade/Clamp conversions
    convert_abs(output_dir)
    convert_check_negative(output_dir)
    convert_kill_nan(output_dir)
    convert_kill_inf(output_dir)
    convert_alpha_binary(output_dir)

    # OSL despill conversions
    convert_despill_green(output_dir)
    convert_despill_blue(output_dir)

    print()
    print(f"Done! Converted {19} files to {output_dir}/")


if __name__ == "__main__":
    main()
