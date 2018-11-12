// -*- c++ -*-
// The light source is placed at the center of lattice
// (which corresponds to the center of the image.)
// I used Adobe Illustrator to add the lens flare in the following cover picture.
// http://onlinelibrary.wiley.com/doi/10.1002/jcc.v39.1/issuetoc

#include "glass.inc"
#include "colors.inc"
#include "shapes.inc"
#include "textures.inc"


      /*
  global_settings {
    radiosity {
      pretrace_start 0.08
      pretrace_end   0.04
      count 35

      nearest_count 5
      error_bound 1.8
      recursion_limit 3

      low_error_factor 0.5
      gray_threshold 0.0
      minimum_reuse 0.015
      brightness 1

      adc_bailout 0.01/2
    }
  }
*/
global_settings { max_trace_level 100} 

#declare RO = 0.0075;
#declare RMe = 0.05;
#declare RNc = 0.05;
#declare RC = 0.015;
#declare RBr = 0.05;
#declare RMa = 0.05;
#declare RMb = 0.05;
#declare RMc = 0.05;
#declare RMd = 0.05;

#declare RH = 0.03;
#declare ROH = 0.02;
#declare RHB = 0.015;
//light_source { <1.7,1.5,-1000> 4.0 } //bottom light
light_source { <1000,1000,1000> 1 } //top light

#declare enable_focus=0;
#declare draw_detail = 0;
#declare draw_media=0;
#declare enable_radiosity=1;
#declare enable_focus=0;


#if (enable_radiosity=1)
global_settings {
  radiosity {   }
}
#end
#declare LOOKAT=<0,0,46>;

camera {
  location LOOKAT + 20*z // (8-0.7)*<0, 1, 1/tan(45*3.14/180/2)>
    look_at LOOKAT
    sky y
    right x
#if (enable_focus=1)
    focal_point < 0,0,0>
    aperture 0.05    
    blur_samples 30
#end
    angle 45+5  //2.7
    }

#declare INTOH = interior { ior 1.0 }
#declare INTG = interior { 
ior 1.0  //1.1 water
}
#declare INTHB = INTG;

#declare FA = finish {
    diffuse 1
    ambient 0
    specular 1
    roughness 0.005
}

#declare FW = finish {
    diffuse 0
    ambient 0
    specular 0
}

#declare Metal = finish {
//diffuse 0
//ambient 0
    specular .5
    //roughness 0.005
}

#declare TEXO = texture {
  pigment {
    rgb <1,1,1>
  }
  finish {Metal}
}
#declare TEXOH = texture {
  pigment {
    rgb <1,1,1>
  }
  finish {FA}
}
#declare TEXH = texture {
  pigment {
    rgb <0,0.7,1>
  }
  finish {FA}
}
#declare TEXMe = texture {
  pigment {
    rgb <0,1,0.05>
  }
  finish {FA}
}
#declare TEXNc = texture {
  pigment {
    rgb <0,1,0.5>
  }
  finish {FA}
}
#declare TEXC = texture {
  pigment {
    rgb <0.1,0.1,0.1>
  }
  finish {FA}
}
#declare TEXW = texture {
  pigment {
    rgb <0.0,0.0,0.0>
  }
  finish {FW}
}
#declare TEXBr = texture {
  pigment {
    rgb <1,1,0>
  }
  finish {FA}
}
#declare TEXMa = texture {
  pigment {
    rgb <1,0,1>
  }
  finish {FA}
}


#declare TEXG = texture {
pigment { rgb <0.05,0.4,0.5> transmit 0.85 }
finish {FA}
}

#declare TEXHB = TEXG;



#declare MATHB = material {
texture { TEXHB }
interior { INTHB }
}
  
#declare MATOH = material {
texture { TEXOH }
}

#declare MATO = material {
texture { TEXO }
}

#declare MATH = material {
texture { TEXH }
}

#declare MATMe = material {
texture { TEXMe }
}
#declare MATNc = material {
texture { TEXNc }
}
#declare MATC = material {
texture { TEXC }
}
#declare MATW = material {
texture { TEXW }
}
#declare MATG = material {
//M_Dark_Green_Glass
texture { TEXG }
interior { INTG }
}
#declare MATBr = material {
texture { TEXBr }
}
#declare MATMa = material {
texture { TEXMa }
}
#declare MATMb=MATMa;
#declare MATMc=MATMa;
#declare MATMd=MATMa;



#if (draw_media=1)
sphere{ LOOKAT, 10 
pigment { rgbt 1 } hollow
  interior {
  media {
    //scattering { 1, 0.01 extinction 0.01 } //normal
       scattering { 1, 0.001 extinction 0.01 }
    #if (draw_detail=1)
      intervals 120
      samples 1, 10
      confidence 0.9999
      variance 1/1000
    #else
      intervals 10
      samples 1, 1
      confidence 0.9
      variance 1/100
    #end
    //ratio 0.9
  }
}}
#end


background {
  rgb <1,1,1>
}
