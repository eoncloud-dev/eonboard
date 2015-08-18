# How To Install Pillow 

The guide below only applies to Ubuntu 14.04 LTS, for other linux distribution, please refer [http://pillow.readthedocs.org/en/latest/installation.html][1]

1. `sudo apt-get zlib1g-dev. libfreetype6-dev`. We use pillow to generate captcha, this function needs libfreetype6-dev and zlib1g-dev.  
2.  If you want to check which feature is available, download Pillow source package, execute `python setup build`, after build is over,  it will display something like below:
    ```
        *** TKINTER support not available
        *** JPEG support not available
        *** OPENJPEG (JPEG2000) support not available
        --- ZLIB (PNG/ZIP) support available
        *** LIBTIFF support not available
        --- FREETYPE2 support available
        *** LITTLECMS2 support not available
        *** WEBP support not available
        *** WEBPMUX support not available
    ```
    You can see freetype and zlib supports are available.

3. `pip install Pillow==2.8.2`. It seems that one bug exists in latest Pillow 2.9.0, when use pip to install Pillow 2.9.0, 
    the _imagingft.so cannot be generated, while the same problem not happend on Pillow 2.8.2.


   [1]: http://pillow.readthedocs.org/en/latest/installation.html

