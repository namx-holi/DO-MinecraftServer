...

SERVER_GB = 4


init_script = f"""
## SETTING UP BLOCK STORAGE ##

# Mount the drive
mkdir -p /mnt/mc
mount -o discard,defaults,noatime /dev/disk/by-id/scsi-0DO_Volume_{volume_name} /mnt/mc



## INSTALLING JAVA FOR FIRST TIME ##

# Download the JDK - https://www.oracle.com/java/technologies/downloads/
wget -P /mnt/mc https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz

# Extract archive
tar -xzf /mnt/mc/jdk*.tar.gz
rm /mnt/mc/jdk*.tar.gz
mv /mnt/mc/jdk* /mnt/mc/jdk



## SETTING UP MINECRAFT SERVER ##

# Set up a directory for all server stuff
mkdir -p /mnt/mc/MinecraftServer

# Get the minecraft server jar
wget -P /mnt/mc/MinecraftServer https://launcher.mojang.com/v1/objects/3cf24a8694aca6267883b17d934efacc5e44440d/server.jar

# Create script to start the server
echo -e '#!/bin/sh\ncd /mnt/mc/MinecraftServer\n/mnt/mc/jdk/bin/java -jar server.jar --nogui' > /mnt/mc/start.sh
chmod +x /mnt/mc/start.sh

# Run the server for the first time
/mnt/mc/start.sh

# Edit the EULA
sed -i 's/false/true/g' /mnt/mc/MinecraftServer/eula.txt

# Edit the start script to start with certain flags!
echo -e '#!/bin/sh\ncd /mnt/mc/MinecraftServer\n/mnt/mc/jdk/bin/java -Xmx{SERVER_GB}G -jar server.jar --nogui' > /mnt/mc/start.sh
"""







reinstall_java_script = f"""
# Remove old jdk
rm -rf jdk

# Redownload and extract new jdk
wget -P /mnt/mc https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz
tar -xzf /mnt/mc/jdk*.tar.gz
rm /mnt/mc/jdk*.tar.gz
mv /mnt/mc/jdk* /mnt/mc/jdk
"""
