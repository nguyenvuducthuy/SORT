case "$(uname -s)" in

Darwin)
rm -rf dependencies
mkdir dependencies
cd dependencies
curl -o easy_profiler.zip http://45.63.123.194/sort_dependencies/mac/easy_profiler.zip
unzip easy_profiler.zip
rm -rf __MACOSX
rm easy_profiler.zip
cd ..
ls
mkdir _out
cd _out
;;

*)
echo 'other OS'
;;
esac
