require 'net/http'
require 'uri'
require 'nokogiri'
require 'json'

urls = [
    'http://robotframework.googlecode.com/hg/doc/libraries/BuiltIn.html?r=2.7.5',
    'http://robotframework.googlecode.com/hg/doc/libraries/Collections.html?r=2.7.5',
    'http://robotframework.googlecode.com/hg/doc/libraries/Dialogs.html?r=2.7.5',
    'http://robotframework.googlecode.com/hg/doc/libraries/OperatingSystem.html?r=2.7.5',
    'http://robotframework.googlecode.com/hg/doc/libraries/Screenshot.html?r=2.7.5',
    'http://robotframework.googlecode.com/hg/doc/libraries/String.html?r=2.7.5',
    'http://robotframework.googlecode.com/hg/doc/libraries/Telnet.html?r=2.7.5',
    'http://robotframework.googlecode.com/hg/doc/libraries/XML.html?r=2.7.5',
    'http://rtomac.github.com/robotframework-selenium2library/doc/Selenium2Library.html',
    'http://robotframework-seleniumlibrary.googlecode.com/hg/doc/SeleniumLibrary.html'
]

def write_json(name, url, keywords)
  json = {"url" => url, "keywords" => keywords}
  out_file = "#{name}.json"
  puts "writing to #{out_file}"
  File.open(out_file, 'wb') do |f|
    output = JSON.pretty_generate json, {:indent => '    '}
    f.write(output + "\n")
  end
end

def process_library(url)
  uri = URI.parse(url)
  http = Net::HTTP.new(uri.host, uri.port)
  response = http.request(Net::HTTP::Get.new(uri.request_uri))
  doc = Nokogiri::HTML(response.body)

  puts "processing #{url}"
  h1 = doc.css('h1').text
  if h1 == 'Opening library documentation failed'
    puts 'detected javascript doc format'

    doc.css('script').each do |script|
      if script.text.include? 'libdoc ='
        text = script.text.strip
        text.slice! 'libdoc = '
        text = text[0..-2] if text[-1] == ';'

        json = JSON.parse(text)
        keywords = json['keywords']
        keywords.each { |key| key.delete 'doc' }

        write_json json['name'], url, keywords
        puts
      end
    end
  end
end

urls.each do |url|
  process_library(url)
end
