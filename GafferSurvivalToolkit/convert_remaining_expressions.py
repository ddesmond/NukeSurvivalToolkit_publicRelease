#!/usr/bin/env python3
"""Convert remaining Expression-based demos to Gaffer node graphs."""

import os
from pathlib import Path


def write_gfr(output_path, content):
    with open(output_path, "w") as f:
        f.write(content)
    print(f"  Created {Path(output_path).name}")


def convert_lines_horizontal(output_dir):
    """Nuke: cos(y/wide) lines → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'float wide = 3.0;\\nfloat thickness = 1.0;\\nfloat c = ( cos( v * 1080.0 / wide ) + thickness ) / 2.0;\\noutput1 = color( c, c, c );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "Lines_Horizontal.gfr"), content)


def convert_lines_vertical(output_dir):
    """Nuke: sin(x/wide) lines → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'float wide = 3.0;\\nfloat thickness = 1.0;\\nfloat c = ( sin( u * 1920.0 / wide ) + thickness ) / 2.0;\\noutput1 = color( c, c, c );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "Lines_Vertical.gfr"), content)


def convert_lines_horizontal_animated(output_dir):
    """Nuke: animated horizontal lines → Gaffer: OSLImage + OSLCode (with frame)"""
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
__children["OSLCode"]["code"].setValue( 'float wide = 3.0;\\nfloat thickness = 1.0;\\nfloat offset = context( "frame" ) * 0.1;\\nfloat c = ( cos( (v * 1080.0 + offset) / wide ) + thickness ) / 2.0;\\noutput1 = color( c, c, c );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "Lines_Horizontal_Animated.gfr"), content)


def convert_lines_vertical_animated(output_dir):
    """Nuke: animated vertical lines → Gaffer: OSLImage + OSLCode (with frame)"""
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
__children["OSLCode"]["code"].setValue( 'float wide = 3.0;\\nfloat thickness = 1.0;\\nfloat offset = context( "frame" ) * 0.1;\\nfloat c = ( sin( (u * 1920.0 + offset) / wide ) + thickness ) / 2.0;\\noutput1 = color( c, c, c );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "Lines_Vertical_Animated.gfr"), content)


def convert_radial(output_dir):
    """Nuke: size - sqrt(x*x + y*y) → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'float size = 600.0;\\nfloat dx = (u - 0.5) * 1920.0;\\nfloat dy = (v - 0.5) * 1080.0;\\nfloat c = size - sqrt( dx * dx + dy * dy );\\noutput1 = color( c, c, c );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "radial.gfr"), content)


def convert_trunc(output_dir):
    """Nuke: trunc(r*scale)/scale → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( 0.5, 0.5, 0.5, 1 ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat scale = 1.0;\\noutput1 = color( trunc( c.r * scale ) / scale, trunc( c.g * scale ) / scale, trunc( c.b * scale ) / scale );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "Trunc.gfr"), content)


def convert_stmap_invert(output_dir):
    """Nuke: STMap invert → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat u_norm = u;\\nfloat v_norm = v;\\nfloat r_out = ((u_norm + 0.5) * 1920.0) / 1920.0 - c.r + ((u_norm + 0.5) * 1920.0) / 1920.0;\\nfloat g_out = ((v_norm + 0.5) * 1080.0) / 1080.0 - c.g + ((v_norm + 0.5) * 1080.0) / 1080.0;\\noutput1 = color( r_out, g_out, 0.0 );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "STMap_invert.gfr"), content)


def convert_uv_to_vector(output_dir):
    """Nuke: UV to Vector → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat u_out = (c.r - (u + 0.5)) * 1920.0;\\nfloat v_out = (c.g - (v + 0.5)) * 1080.0;\\noutput1 = color( u_out, v_out, 0.0 );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "UV_to_Vector.gfr"), content)


def convert_vector_to_uv(output_dir):
    """Nuke: Vector to UV → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat u_out = (c.r + u + 0.5) / 1920.0;\\nfloat v_out = (c.g + v + 0.5) / 1080.0;\\noutput1 = color( u_out, v_out, 0.0 );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "Vector_to_UV.gfr"), content)


def convert_alpha_comparison(output_dir):
    """Nuke: alpha < number → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( 0.5, 0.5, 0.5, 0.3 ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat threshold = 0.1;\\nfloat mask = c.a < threshold ? 1.0 : 0.0;\\noutput1 = color( c.r * mask, c.g * mask, c.b * mask );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "alpha_comparison.gfr"), content)


def convert_alpha_sum(output_dir):
    """Nuke: r+g+b to alpha → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( 0.3, 0.5, 0.2, 1 ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "A", Gaffer.FloatPlug( "value", defaultValue = 1.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.FloatPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = 0.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat sum = c.r + c.g + c.b;\\noutput1 = clamp( sum, 0.0, 1.0 );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "alpha_sum.gfr"), content)


def convert_despill_green_list(output_dir):
    """Nuke: despill green list → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
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
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat key = max( 0.0, c.g - (c.r + c.b) / 2.0 );\\nc.g = c.g - key * 0.5;\\nc.r = c.r + key * 0.25;\\nc.b = c.b + key * 0.25;\\noutput1 = c.rgb;' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "despill_green_list.gfr"), content)


def convert_despill_blue_list(output_dir):
    """Nuke: despill blue list → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat key = max( 0.0, c.b - (c.r + c.g) / 2.0 );\\nc.b = c.b - key * 0.5;\\nc.r = c.r + key * 0.25;\\nc.g = c.g + key * 0.25;\\noutput1 = c.rgb;' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "despill_blue_list.gfr"), content)


def convert_random_colors(output_dir):
    """Nuke: random(r), random(g), random(b) → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\noutput1 = color( cellnoise( c.r * 1000.0 ), cellnoise( c.g * 1000.0 ), cellnoise( c.b * 1000.0 ) );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "Random_colors.gfr"), content)


def convert_random_every_frame(output_dir):
    """Nuke: random(frame) → Gaffer: OSLImage + OSLCode (frame-based)"""
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
__children["OSLCode"]["code"].setValue( 'float f = context( "frame" );\\nfloat r = cellnoise( f * 123.456 );\\noutput1 = color( r, r, r );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "Random_every_frame.gfr"), content)


def convert_random_every_pixel(output_dir):
    """Nuke: random per pixel → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'float r = cellnoise( u * 10000.0, v * 10000.0 );\\noutput1 = color( r, r, r );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "Random_every_pixel.gfr"), content)


def convert_transform(output_dir):
    """Nuke: transform with translate/scale → Gaffer: ImageTransform"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( 0.5, 0.3, 0.7, 1 ) )

__children["ImageTransform"] = GafferImage.ImageTransform( "ImageTransform" )
parent.addChild( __children["ImageTransform"] )
__children["ImageTransform"]["in"].setInput( __children["Constant"]["out"] )
__children["ImageTransform"]["translate"].setValue( imath.V2f( 410, 440 ) )
__children["ImageTransform"]["scale"].setValue( imath.V2f( 2, 2 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "transform.gfr"), content)


def convert_transform_advanced(output_dir):
    """Nuke: transform with rotation → Gaffer: ImageTransform"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( 0.5, 0.3, 0.7, 1 ) )

__children["ImageTransform"] = GafferImage.ImageTransform( "ImageTransform" )
parent.addChild( __children["ImageTransform"] )
__children["ImageTransform"]["in"].setInput( __children["Constant"]["out"] )
__children["ImageTransform"]["translate"].setValue( imath.V2f( 0, 0 ) )
__children["ImageTransform"]["rotate"].setValue( 0 )
__children["ImageTransform"]["scale"].setValue( imath.V2f( 1, 1 ) )
__children["ImageTransform"]["center"].setValue( imath.V2f( 960, 540 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "transform_advanced.gfr"), content)


def convert_keying(output_dir):
    """Nuke: keying expression → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
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
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "A", Gaffer.FloatPlug( "value", defaultValue = 1.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.FloatPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = 0.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat sum = c.r + c.g + c.b;\\nfloat ratio_r = c.r / (sum + 0.001);\\nfloat ratio_g = c.g / (sum + 0.001);\\nfloat ratio_b = c.b / (sum + 0.001);\\nfloat target_r = 0.2;\\nfloat target_g = 0.8;\\nfloat target_b = 0.3;\\nfloat diff = abs( ratio_r - target_r ) + abs( ratio_g - target_g ) + abs( ratio_b - target_b );\\nfloat matte = clamp( 1.0 - diff * 3.0, 0.0, 1.0 );\\noutput1 = matte;' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "keying.gfr"), content)


def convert_points(output_dir):
    """Nuke: points pattern → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'float offsetX = 200.0;\\nfloat offsetY = 200.0;\\nfloat value = 1.0;\\nfloat px = floor( u * 1920.0 );\\nfloat py = floor( v * 1080.0 );\\nfloat isPoint = ( mod( px, offsetX ) == 0 && mod( py, offsetY ) == 0 ) ? value : 0.0;\\noutput1 = color( isPoint, isPoint, isPoint );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "points.gfr"), content)


def convert_points_advanced(output_dir):
    """Nuke: points advanced → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'float offsetX = 135.0;\\nfloat offsetY = 181.0;\\nfloat offset = 87.0;\\nfloat gain = 1.0;\\nfloat px = floor( u * 1920.0 );\\nfloat py = floor( v * 1080.0 );\\nfloat isPoint = ( mod( py, offsetX ) == 0 && mod( px + offset, offsetY ) == 0 ) ? gain : 0.0;\\nfloat r = cellnoise( px, py, 1.0 ) * isPoint;\\nfloat g = cellnoise( px, py, 2.0 ) * isPoint;\\nfloat b = cellnoise( px, py, 3.0 ) * isPoint;\\noutput1 = color( r, g, b );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "points_advanced.gfr"), content)


def convert_normalpass_relight(output_dir):
    """Nuke: normal pass relight → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( 0.5, 0.5, 0.5, 1 ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "A", Gaffer.FloatPlug( "value", defaultValue = 1.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.FloatPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = 0.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'color n = inLayer( "rgba" );\\nvector lightDir = normalize( vector( 0.5, 0.5, 1.0 ) );\\nvector normal = normalize( vector( n.r * 2.0 - 1.0, n.g * 2.0 - 1.0, n.b * 2.0 - 1.0 ) );\\nfloat diffuse = max( 0.0, dot( normal, lightDir ) );\\noutput1 = diffuse;' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "normalPass_relight.gfr"), content)


def convert_deep_to_depth(output_dir):
    """Nuke: deep to depth → Gaffer: DeepState + Grade"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )

__children["DeepState"] = GafferImage.DeepState( "DeepState" )
parent.addChild( __children["DeepState"] )
__children["DeepState"]["in"].setInput( __children["Constant"]["out"] )
__children["DeepState"]["mode"].setValue( GafferImage.DeepState.Mode.Front )

del __children
"""
    write_gfr(os.path.join(output_dir, "deepToDepth.gfr"), content)


def convert_depth_normalize(output_dir):
    """Nuke: depth normalize (1/z) → Gaffer: OSLImage + OSLCode"""
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
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "depth", Gaffer.FloatPlug( "value", defaultValue = 1.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.FloatPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = 0.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'float z = inChannel( "depth" );\\noutput1 = (z == 0.0) ? 0.0 : 1.0 / z;' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "depth_normalize.gfr"), content)


def convert_create_nan(output_dir):
    """Nuke: create NaN → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'float nan = 0.0 / 0.0;\\noutput1 = color( nan, nan, nan );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "create_nan.gfr"), content)


def convert_create_inf(output_dir):
    """Nuke: create inf → Gaffer: OSLImage + OSLCode"""
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
__children["OSLCode"]["code"].setValue( 'float inf = 1.0 / 0.0;\\noutput1 = color( inf, inf, inf );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "create_inf.gfr"), content)


def convert_check_nan_inf(output_dir):
    """Nuke: check nan/inf → Gaffer: OSLImage + OSLCode"""
    content = """import Gaffer
import GafferImage
import GafferOSL
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( 1e38, 0.0/0.0, 1.0/0.0, 1 ) )

__children["OSLImage"] = GafferOSL.OSLImage( "OSLImage" )
parent.addChild( __children["OSLImage"] )
__children["OSLImage"]["in"].setInput( __children["Constant"]["out"] )
__children["OSLImage"]["channels"].addChild( Gaffer.NameValuePlug( "", Gaffer.Color3fPlug( "value", defaultValue = imath.Color3f( 1, 1, 1 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ), True, "channel", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

__children["OSLCode"] = GafferOSL.OSLCode( "OSLCode" )
parent.addChild( __children["OSLCode"] )
__children["OSLCode"]["out"].addChild( Gaffer.Color3fPlug( "output1", direction = Gaffer.Plug.Direction.Out, defaultValue = imath.Color3f( 0, 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
__children["OSLCode"]["code"].setValue( 'color c = inLayer( "rgba" );\\nfloat is_nan = isnan( c.r ) || isnan( c.g ) || isnan( c.b );\\nfloat is_inf = isinf( c.r ) || isinf( c.g ) || isinf( c.b );\\nfloat mask = is_nan || is_inf ? 1.0 : 0.0;\\noutput1 = color( mask, mask, mask );' )

__children["OSLImage"]["channels"]["channel"]["value"].setInput( __children["OSLCode"]["out"]["output1"] )
__children["OSLImage"]["channels"]["channel"]["value"]["r"].setInput( __children["OSLCode"]["out"]["output1"]["r"] )
__children["OSLImage"]["channels"]["channel"]["value"]["g"].setInput( __children["OSLCode"]["out"]["output1"]["g"] )
__children["OSLImage"]["channels"]["channel"]["value"]["b"].setInput( __children["OSLCode"]["out"]["output1"]["b"] )

del __children
"""
    write_gfr(os.path.join(output_dir, "check_nan_inf.gfr"), content)


def convert_c4x4(output_dir):
    """Nuke: C4x4 matrix transform → Gaffer: ImageTransform"""
    content = """import Gaffer
import GafferImage
import IECore
import imath

__children = {}

__children["Constant"] = GafferImage.Constant( "Constant" )
parent.addChild( __children["Constant"] )
__children["Constant"]["format"].setValue( Gaffer.Format( 1920, 1080, 1.0, "HD_1080" ) )
__children["Constant"]["color"].setValue( imath.Color4f( 0.5, 0.3, 0.7, 1 ) )

__children["ImageTransform"] = GafferImage.ImageTransform( "ImageTransform" )
parent.addChild( __children["ImageTransform"] )
__children["ImageTransform"]["in"].setInput( __children["Constant"]["out"] )
__children["ImageTransform"]["rotate"].setValue( 32 )
__children["ImageTransform"]["center"].setValue( imath.V2f( 960, 540 ) )

del __children
"""
    write_gfr(os.path.join(output_dir, "C4x4.gfr"), content)


def main():
    output_dir = "demo"
    os.makedirs(output_dir, exist_ok=True)

    print("Converting remaining Expression-based demos to Gaffer .gfr...")
    print()

    # Lines patterns
    convert_lines_horizontal(output_dir)
    convert_lines_vertical(output_dir)
    convert_lines_horizontal_animated(output_dir)
    convert_lines_vertical_animated(output_dir)

    # Radial
    convert_radial(output_dir)

    # Trunc
    convert_trunc(output_dir)

    # STMap/UV/Vector conversions
    convert_stmap_invert(output_dir)
    convert_uv_to_vector(output_dir)
    convert_vector_to_uv(output_dir)

    # Alpha operations
    convert_alpha_comparison(output_dir)
    convert_alpha_sum(output_dir)

    # Despill list variants
    convert_despill_green_list(output_dir)
    convert_despill_blue_list(output_dir)

    # Random patterns
    convert_random_colors(output_dir)
    convert_random_every_frame(output_dir)
    convert_random_every_pixel(output_dir)

    # Transform
    convert_transform(output_dir)
    convert_transform_advanced(output_dir)

    # Keying
    convert_keying(output_dir)

    # Points patterns
    convert_points(output_dir)
    convert_points_advanced(output_dir)

    # Normal pass relight
    convert_normalpass_relight(output_dir)

    # Deep operations
    convert_deep_to_depth(output_dir)
    convert_depth_normalize(output_dir)

    # NaN/Inf operations
    convert_create_nan(output_dir)
    convert_create_inf(output_dir)
    convert_check_nan_inf(output_dir)

    # C4x4
    convert_c4x4(output_dir)

    print()
    print(f"Done! Converted {29} files to {output_dir}/")


if __name__ == "__main__":
    main()
